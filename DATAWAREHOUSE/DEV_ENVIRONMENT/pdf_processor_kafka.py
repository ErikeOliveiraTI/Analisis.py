#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF to Excel Converter - Kafka Consumer
========================================

Responsável por:
  ✓ Escutar tópico 'backup-events' do Kafka
  ✓ Detectar PDFs na pasta de backup
  ✓ Converter PDFs para Excel (.xlsx)
  ✓ Atualizar metadados no DW
  ✓ Enviar eventos de conclusão/erro

Uso:
  python pdf_processor_kafka.py
  
Tópicos Consumidos:
  - backup-events
  
Tópicos Publicados:
  - data-warehouse-events (status conversão)
  - alerts (erros de processamento)

Dependências:
  - pip install pdfplumber openpyxl
"""

import json
import logging
import platform
import sys
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import hashlib

try:
    from kafka import KafkaConsumer, KafkaProducer
    KAFKA_DISPONIVEL = True
except ImportError:
    KAFKA_DISPONIVEL = False
    print("⚠️  Kafka não instalado")
    sys.exit(1)

try:
    import pdfplumber
    import openpyxl
    from openpyxl.utils import get_column_letter
    PDF_LIBS_OK = True
except ImportError:
    PDF_LIBS_OK = False
    print("⚠️  pdfplumber ou openpyxl não instalado")
    print("   Execute: pip install pdfplumber openpyxl")

import pandas as pd

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

class ConfigPDFConsumer:
    """Configuração centralizada"""
    
    if platform.system() == "Windows":
        BASE_DIR = Path("z:/git/rotina")
        LOG_DIR = Path("z:/git/rotina/log")
    else:
        BASE_DIR = Path("/mnt/z/git/rotina")
        LOG_DIR = Path("/mnt/z/git/rotina/log")
    
    LOG_FILE = LOG_DIR / f"pdf_processor_kafka_{datetime.now().strftime('%Y-%m-%d')}.log"
    
    # Kafka
    KAFKA_BROKERS = "localhost:9092"
    CONSUMER_GROUP = "pdf-processor-group"
    TOPICO_INPUT = "backup-events"
    TOPICO_OUTPUT = "data-warehouse-events"
    TOPICO_ALERTAS = "alerts"
    
    # PDF processing
    EXTENSOES_PDF = ['.pdf']
    EXTENSOES_SUPORTE = ['.xlsx', '.xls', '.csv']


# ============================================================================
# LOGGER
# ============================================================================

def configurar_logger():
    """Configura logging"""
    ConfigPDFConsumer.LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger("PDFProcessorKafka")
    logger.setLevel(logging.DEBUG)
    
    fh = logging.FileHandler(ConfigPDFConsumer.LOG_FILE, encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    
    formato = logging.Formatter(
        '[%(asctime)s] [%(levelname)-8s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    fh.setFormatter(formato)
    ch.setFormatter(formato)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger

logger = configurar_logger()


# ============================================================================
# PDF CONVERTER
# ============================================================================

class PDFtoExcelConverter:
    """Converte PDFs para Excel com extração de dados"""
    
    def __init__(self):
        """Inicializa converter"""
        self.suporta_pdf = PDF_LIBS_OK
        
        if self.suporta_pdf:
            logger.info("✓ PDF Libs disponíveis (pdfplumber + openpyxl)")
        else:
            logger.warning("⚠️  PDF Libs não disponíveis - modo fallback")
    
    def extrair_texto_pdf(self, caminho_pdf: Path) -> str:
        """
        Extrai texto de PDF
        
        Args:
            caminho_pdf: Path do arquivo PDF
            
        Returns:
            Texto extraído
        """
        if not self.suporta_pdf:
            return "[Texto não extraído - biblioteca não disponível]"
        
        try:
            texto = ""
            with pdfplumber.open(str(caminho_pdf)) as pdf:
                for i, page in enumerate(pdf.pages):
                    texto += f"\n{'='*80}\nPÁGINA {i+1}\n{'='*80}\n"
                    texto += page.extract_text() or "[Página vazia]"
            return texto
        except Exception as e:
            logger.error(f"Erro ao extrair texto: {str(e)}")
            return f"[Erro ao extrair: {str(e)}]"
    
    def extrair_tabelas_pdf(self, caminho_pdf: Path) -> Optional[pd.DataFrame]:
        """
        Extrai tabelas de PDF e retorna como DataFrame
        
        Args:
            caminho_pdf: Path do arquivo PDF
            
        Returns:
            DataFrame com dados tabulares, ou None
        """
        if not self.suporta_pdf:
            return None
        
        try:
            with pdfplumber.open(str(caminho_pdf)) as pdf:
                tabelas = []
                for page_num, page in enumerate(pdf.pages):
                    page_tables = page.extract_tables()
                    if page_tables:
                        for table in page_tables:
                            df = pd.DataFrame(table)
                            tabelas.append(df)
                
                if tabelas:
                    df_final = pd.concat(tabelas, ignore_index=True)
                    logger.info(f"✓ Extraídas {len(tabelas)} tabelas com {len(df_final)} linhas")
                    return df_final
                else:
                    logger.warning("⚠️  Nenhuma tabela encontrada no PDF")
                    return None
                    
        except Exception as e:
            logger.error(f"Erro ao extrair tabelas: {str(e)}")
            return None
    
    def converter_para_excel(self, caminho_pdf: Path, caminho_excel: Path) -> bool:
        """
        Converte PDF para Excel com múltiplas abas
        
        Args:
            caminho_pdf: Path do arquivo PDF
            caminho_excel: Path de destino (.xlsx)
            
        Returns:
            True se sucesso, False se erro
        """
        try:
            # Verificar se PDF existe
            if not caminho_pdf.exists():
                logger.error(f"✗ Arquivo PDF não encontrado: {caminho_pdf}")
                return False
            
            logger.info(f"▶ Convertendo: {caminho_pdf.name} → {caminho_excel.name}")
            
            # Criar workbook
            workbook = openpyxl.Workbook()
            workbook.remove(workbook.active)  # Remove sheet padrão
            
            # Aba 1: Informações
            ws_info = workbook.create_sheet("Informações")
            ws_info['A1'] = "Origem PDF:"
            ws_info['B1'] = str(caminho_pdf)
            ws_info['A2'] = "Data Conversão:"
            ws_info['B2'] = datetime.now().isoformat()
            ws_info['A3'] = "Tamanho Original:"
            ws_info['B3'] = f"{caminho_pdf.stat().st_size / 1024:.2f} KB"
            
            # Aba 2: Texto extraído
            ws_texto = workbook.create_sheet("Texto")
            texto = self.extrair_texto_pdf(caminho_pdf)
            # Dividir em linhas para caber em células
            for i, linha in enumerate(texto.split('\n')[:1000]):  # Limit 1000 linhas
                ws_texto[f'A{i+1}'] = linha[:32767]  # Excel limit
            
            # Aba 3: Tabelas (se existirem)
            df_tabelas = self.extrair_tabelas_pdf(caminho_pdf)
            if df_tabelas is not None:
                ws_tabelas = workbook.create_sheet("Tabelas")
                for r_idx, row in enumerate(df_tabelas.values, 1):
                    for c_idx, value in enumerate(row, 1):
                        ws_tabelas.cell(r_idx + 1, c_idx, value)
                
                # Adicionar header
                for c_idx, col_name in enumerate(df_tabelas.columns, 1):
                    ws_tabelas.cell(1, c_idx, str(col_name))
            
            # Salvar
            workbook.save(str(caminho_excel))
            logger.info(f"✓ Convertido com sucesso: {caminho_excel}")
            
            return True
            
        except Exception as e:
            logger.error(f"✗ Erro na conversão: {str(e)}")
            return False


# ============================================================================
# PDF PROCESSOR CONSUMER
# ============================================================================

class PDFProcessorConsumer:
    """Consumer Kafka para processar PDFs"""
    
    def __init__(self):
        """Inicializa consumer"""
        try:
            self.consumer = KafkaConsumer(
                ConfigPDFConsumer.TOPICO_INPUT,
                bootstrap_servers=ConfigPDFConsumer.KAFKA_BROKERS,
                group_id=ConfigPDFConsumer.CONSUMER_GROUP,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                auto_offset_reset='earliest',
                enable_auto_commit=False
            )
            
            self.producer = KafkaProducer(
                bootstrap_servers=ConfigPDFConsumer.KAFKA_BROKERS,
                value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8')
            )
            
            self.converter = PDFtoExcelConverter()
            
            logger.info("✓ PDF Processor Consumer inicializado")
            logger.info(f"  Broker: {ConfigPDFConsumer.KAFKA_BROKERS}")
            logger.info(f"  Consumer Group: {ConfigPDFConsumer.CONSUMER_GROUP}")
            
        except Exception as e:
            logger.error(f"✗ Erro ao inicializar: {str(e)}")
            raise
    
    def encontrar_pdfs(self, data_pasta: str) -> List[Path]:
        """
        Encontra todos os PDFs na pasta de backup
        
        Args:
            data_pasta: Nome da pasta (ex: "05 APR")
            
        Returns:
            Lista de Paths dos PDFs encontrados
        """
        pasta = ConfigPDFConsumer.BASE_DIR / data_pasta
        
        if not pasta.exists():
            logger.warning(f"⚠️  Pasta não encontrada: {pasta}")
            return []
        
        pdfs = list(pasta.glob("**/*.pdf"))
        logger.info(f"✓ Encontrados {len(pdfs)} PDFs em {data_pasta}")
        
        return pdfs
    
    def processar_pdfs_paralelo(self, data_pasta: str) -> Dict[str, Any]:
        """
        Processa todos os PDFs de uma pasta
        
        Args:
            data_pasta: Nome da pasta (ex: "05 APR")
            
        Returns:
            Dict com resultado do processamento
        """
        tempo_inicio = datetime.now()
        pdfs = self.encontrar_pdfs(data_pasta)
        
        resultados = {
            'total_pdfs': len(pdfs),
            'convertidos': 0,
            'erros': 0,
            'arquivos': []
        }
        
        for pdf_path in pdfs:
            excel_path = pdf_path.with_suffix('.xlsx')
            
            try:
                logger.info(f"  Processando: {pdf_path.name}")
                
                sucesso = self.converter.converter_para_excel(pdf_path, excel_path)
                
                if sucesso:
                    resultados['convertidos'] += 1
                    resultados['arquivos'].append({
                        'pdf': str(pdf_path),
                        'excel': str(excel_path),
                        'status': 'sucesso',
                        'tamanho_excel': excel_path.stat().st_size
                    })
                    
                    # Enviar evento de sucesso
                    self.producer.send(ConfigPDFConsumer.TOPICO_OUTPUT, {
                        'tipo_operacao': 'PDF_CONVERTIDO',
                        'arquivo_pdf': str(pdf_path),
                        'arquivo_excel': str(excel_path),
                        'status': 'sucesso',
                        'data_pasta': data_pasta
                    })
                else:
                    resultados['erros'] += 1
                    resultados['arquivos'].append({
                        'pdf': str(pdf_path),
                        'status': 'erro',
                        'mensagem': 'Falha na conversão'
                    })
                    
                    # Enviar alerta
                    self.producer.send(ConfigPDFConsumer.TOPICO_ALERTAS, {
                        'severidade': 'warning',
                        'tipo': 'pdf_conversion_error',
                        'titulo': f'Erro ao converter PDF',
                        'descricao': f'Não foi possível converter {pdf_path.name}',
                        'arquivo': str(pdf_path)
                    })
                    
            except Exception as e:
                logger.error(f"  ✗ Erro crítico: {str(e)}")
                resultados['erros'] += 1
        
        duracao = (datetime.now() - tempo_inicio).total_seconds()
        resultados['duracao_segundos'] = duracao
        
        logger.info(f"✓ Processamento concluído: {resultados['convertidos']} OK, {resultados['erros']} erros em {duracao:.2f}s")
        
        return resultados
    
    def processar_evento(self, evento: Dict[str, Any]) -> bool:
        """
        Processa evento de backup para extrair PDFs
        
        Args:
            evento: Dict com dados do evento
            
        Returns:
            True se processado com sucesso
        """
        tipo = evento.get('tipo')
        data_pasta = evento.get('data_pasta')
        
        if tipo != 'backup_concluido':
            return True  # Ignorar eventos que não são conclusão de backup
        
        try:
            logger.info(f"▶ Processando PDFs de: {data_pasta}")
            
            resultado = self.processar_pdfs_paralelo(data_pasta)
            
            # Enviar resumo
            self.producer.send(ConfigPDFConsumer.TOPICO_OUTPUT, {
                'tipo_operacao': 'PDF_BATCH_PROCESSADO',
                'data_pasta': data_pasta,
                'total_pdfs': resultado['total_pdfs'],
                'convertidos': resultado['convertidos'],
                'erros': resultado['erros'],
                'duracao_segundos': resultado['duracao_segundos']
            })
            
            return True
            
        except Exception as e:
            logger.error(f"✗ Erro ao processar PDFs: {str(e)}")
            
            self.producer.send(ConfigPDFConsumer.TOPICO_ALERTAS, {
                'severidade': 'error',
                'tipo': 'pdf_processing_error',
                'titulo': 'Erro crítico em PDF Processing',
                'descricao': str(e),
                'data_pasta': data_pasta
            })
            
            return False
    
    def iniciar(self):
        """Loop principal do consumer"""
        
        logger.info("")
        logger.info("=" * 80)
        logger.info("PDF PROCESSOR CONSUMER AGUARDANDO EVENTOS...")
        logger.info("=" * 80)
        logger.info(f"Aguardando eventos em: {ConfigPDFConsumer.TOPICO_INPUT}")
        logger.info("Pressione Ctrl+C para parar")
        logger.info("=" * 80)
        logger.info("")
        
        contador_eventos = 0
        
        try:
            for mensagem in self.consumer:
                try:
                    evento = mensagem.value
                    contador_eventos += 1
                    
                    logger.info(f"[Evento #{contador_eventos}] {evento.get('tipo')}")
                    
                    # Processar evento
                    sucesso = self.processar_evento(evento)
                    
                    if sucesso:
                        self.consumer.commit()
                        logger.info("✓ Evento processado e commitado")
                    else:
                        logger.error("✗ Erro no processamento - sem commit")
                    
                except Exception as e:
                    logger.error(f"✗ Erro ao processar mensagem: {str(e)}")
                    
        except KeyboardInterrupt:
            logger.info("\n▪ PDF Processor interrompido (Ctrl+C)")
        finally:
            self.consumer.close()
            self.producer.close()
            logger.info("✓ PDF Processor Consumer finalizado")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    
    if not KAFKA_DISPONIVEL:
        logger.error("✗ Kafka não disponível")
        sys.exit(1)
    
    if not PDF_LIBS_OK:
        logger.warning("⚠️  Bibliotecas PDF não disponíveis")
        logger.warning("   Execute: pip install pdfplumber openpyxl")
        logger.warning("   Continuando em modo limitado...")
    
    consumer = PDFProcessorConsumer()
    
    try:
        consumer.iniciar()
    except Exception as e:
        logger.critical(f"Erro crítico: {str(e)}")
        sys.exit(1)
