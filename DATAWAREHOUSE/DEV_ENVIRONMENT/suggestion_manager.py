#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerenciador de Sugestões - Windsurf Integration Terminal

Permite aceitar/rejeitar recomendações de melhorias no terminal,
com integração visual e histórico de mudanças.

Uso:
  python suggestion_manager.py
  python suggestion_manager.py --review
  python suggestion_manager.py --history
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import sys

# ============================================================================
# CONFIGURAÇÃO
# ============================================================================

class SuggestionConfig:
    """Configuração do gerenciador de sugestões"""
    
    BASE_DIR = Path(__file__).parent
    SUGGESTIONS_FILE = BASE_DIR / ".suggestions.json"
    HISTORY_FILE = BASE_DIR / ".suggestion_history.json"
    
    # Categorias de sugestões
    CATEGORIES = {
        'optimization': ('⚡', 'Otimização'),
        'security': ('🔒', 'Segurança'),
        'performance': ('🚀', 'Performance'),
        'style': ('📝', 'Estilo'),
        'refactoring': ('🔄', 'Refactoring'),
        'testing': ('✅', 'Testing'),
        'documentation': ('📚', 'Documentação'),
    }
    
    # Cores ANSI
    COLORS = {
        'HEADER': '\033[95m',
        'BLUE': '\033[94m',
        'CYAN': '\033[96m',
        'GREEN': '\033[92m',
        'YELLOW': '\033[93m',
        'RED': '\033[91m',
        'ENDC': '\033[0m',
        'BOLD': '\033[1m',
        'UNDERLINE': '\033[4m',
    }

# ============================================================================
# CLASSE PRINCIPAL
# ============================================================================

class SuggestionManager:
    """Gerenciador de sugestões de melhoria"""
    
    def __init__(self):
        """Inicializa gerenciador"""
        self.suggestions = self._carregar_sugestoes()
        self.history = self._carregar_historico()
    
    # ========================================================================
    # CARREGAR/SALVAR
    # ========================================================================
    
    def _carregar_sugestoes(self) -> List[Dict]:
        """Carrega sugestões do arquivo"""
        if SuggestionConfig.SUGGESTIONS_FILE.exists():
            try:
                with open(SuggestionConfig.SUGGESTIONS_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _carregar_historico(self) -> List[Dict]:
        """Carrega histórico de decisões"""
        if SuggestionConfig.HISTORY_FILE.exists():
            try:
                with open(SuggestionConfig.HISTORY_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _salvar_sugestoes(self):
        """Salva sugestões no arquivo"""
        with open(SuggestionConfig.SUGGESTIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.suggestions, f, indent=2, ensure_ascii=False)
    
    def _salvar_historico(self):
        """Salva histórico no arquivo"""
        with open(SuggestionConfig.HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)
    
    # ========================================================================
    # GERENCIAR SUGESTÕES
    # ========================================================================
    
    def adicionar_sugestao(self, arquivo: str, linha: int, tipo: str, 
                          titulo: str, descricao: str, 
                          antes: str, depois: str) -> None:
        """Adiciona nova sugestão"""
        
        sugestao = {
            "id": len(self.suggestions) + 1,
            "timestamp": datetime.now().isoformat(),
            "arquivo": arquivo,
            "linha": linha,
            "tipo": tipo,
            "titulo": titulo,
            "descricao": descricao,
            "antes": antes,
            "depois": depois,
            "status": "pendente"  # pendente, aceito, rejeitado
        }
        
        self.suggestions.append(sugestao)
        self._salvar_sugestoes()
        
        print(f"{SuggestionConfig.COLORS['GREEN']}✓ Sugestão adicionada (ID: {sugestao['id']}){SuggestionConfig.COLORS['ENDC']}")
    
    def listar_pendentes(self) -> None:
        """Lista sugestões pendentes"""
        pendentes = [s for s in self.suggestions if s['status'] == 'pendente']
        
        if not pendentes:
            print(f"{SuggestionConfig.COLORS['YELLOW']}ℹ Nenhuma sugestão pendente{SuggestionConfig.COLORS['ENDC']}")
            return
        
        print(f"\n{SuggestionConfig.COLORS['BOLD']}{SuggestionConfig.COLORS['HEADER']}")
        print("=" * 80)
        print(f"SUGESTÕES PENDENTES ({len(pendentes)})")
        print("=" * 80)
        print(f"{SuggestionConfig.COLORS['ENDC']}\n")
        
        for idx, sugestao in enumerate(pendentes, 1):
            self._exibir_sugestao(sugestao, idx)
    
    def _exibir_sugestao(self, sugestao: Dict, numero: int = 1) -> None:
        """Exibe uma sugestão formatada"""
        
        icone, categoria = SuggestionConfig.CATEGORIES.get(
            sugestao['tipo'], 
            ('💡', 'Geral')
        )
        
        print(f"{SuggestionConfig.COLORS['CYAN']}{numero}. {icone} {categoria}")
        print(f"{SuggestionConfig.COLORS['ENDC']}", end='')
        
        print(f"   ID: {sugestao['id']}")
        print(f"   Arquivo: {sugestao['arquivo']}:{sugestao['linha']}")
        print(f"   Título: {sugestao['titulo']}")
        print(f"   Descrição: {sugestao['descricao']}")
        
        print(f"\n   {SuggestionConfig.COLORS['YELLOW']}Antes:{SuggestionConfig.COLORS['ENDC']}")
        for linha in sugestao['antes'].split('\n')[:3]:
            print(f"   {linha}")
        
        print(f"\n   {SuggestionConfig.COLORS['GREEN']}Depois:{SuggestionConfig.COLORS['ENDC']}")
        for linha in sugestao['depois'].split('\n')[:3]:
            print(f"   {linha}")
        
        print(f"\n   {SuggestionConfig.COLORS['BOLD']}{'─' * 76}{SuggestionConfig.COLORS['ENDC']}\n")
    
    # ========================================================================
    # REVISAR
    # ========================================================================
    
    def revisar_sugestoes(self) -> None:
        """Interface interativa para revisar sugestões"""
        
        pendentes = [s for s in self.suggestions if s['status'] == 'pendente']
        
        if not pendentes:
            print(f"{SuggestionConfig.COLORS['GREEN']}✓ Nenhuma sugestão para revisar!{SuggestionConfig.COLORS['ENDC']}")
            return
        
        for idx, sugestao in enumerate(pendentes, 1):
            print(f"\n{SuggestionConfig.COLORS['BOLD']}{SuggestionConfig.COLORS['HEADER']}")
            print(f"SUGESTÃO {idx} de {len(pendentes)}")
            print(f"{SuggestionConfig.COLORS['ENDC']}")
            
            self._exibir_sugestao(sugestao)
            
            while True:
                opcao = input(
                    f"{SuggestionConfig.COLORS['BOLD']}"
                    f"[✓] Aceitar | [✗] Rejeitar | [?] Explicar | [S] Pular > "
                    f"{SuggestionConfig.COLORS['ENDC']}"
                ).strip().upper()
                
                if opcao == 'V' or opcao == '✓':
                    self._aceitar_sugestao(sugestao)
                    break
                elif opcao == 'X' or opcao == '✗':
                    self._rejeitar_sugestao(sugestao)
                    break
                elif opcao == '?':
                    print(f"\n{SuggestionConfig.COLORS['BLUE']}Enquanto...)
                    print(f"{sugestao['descricao']}{SuggestionConfig.COLORS['ENDC']}\n")
                elif opcao == 'S':
                    print(f"{SuggestionConfig.COLORS['YELLOW']}⊘ Pulado{SuggestionConfig.COLORS['ENDC']}")
                    break
                else:
                    print(f"{SuggestionConfig.COLORS['RED']}✗ Opção inválida{SuggestionConfig.COLORS['ENDC']}")
    
    def _aceitar_sugestao(self, sugestao: Dict) -> None:
        """Aceita uma sugestão"""
        
        # Atualizar status
        idx = next(i for i, s in enumerate(self.suggestions) if s['id'] == sugestao['id'])
        self.suggestions[idx]['status'] = 'aceito'
        
        # Adicionar ao histórico
        self.history.append({
            "id": sugestao['id'],
            "timestamp": datetime.now().isoformat(),
            "acao": "aceito",
            "arquivo": sugestao['arquivo'],
            "tipo": sugestao['tipo']
        })
        
        # Salvar
        self._salvar_sugestoes()
        self._salvar_historico()
        
        print(f"{SuggestionConfig.COLORS['GREEN']}✓ Sugestão aceita!{SuggestionConfig.COLORS['ENDC']}\n")
    
    def _rejeitar_sugestao(self, sugestao: Dict) -> None:
        """Rejeita uma sugestão"""
        
        # Atualizar status
        idx = next(i for i, s in enumerate(self.suggestions) if s['id'] == sugestao['id'])
        self.suggestions[idx]['status'] = 'rejeitado'
        
        # Adicionar ao histórico
        self.history.append({
            "id": sugestao['id'],
            "timestamp": datetime.now().isoformat(),
            "acao": "rejeitado",
            "arquivo": sugestao['arquivo'],
            "tipo": sugestao['tipo'],
            "motivo": input("Motivo da rejeição (opcional): ").strip() or "N/A"
        })
        
        # Salvar
        self._salvar_sugestoes()
        self._salvar_historico()
        
        print(f"{SuggestionConfig.COLORS['RED']}✗ Sugestão rejeitada{SuggestionConfig.COLORS['ENDC']}\n")
    
    # ========================================================================
    # ESTATÍSTICAS
    # ========================================================================
    
    def mostrar_estatisticas(self) -> None:
        """Mostra estatísticas das sugestões"""
        
        total = len(self.suggestions)
        aceitos = len([s for s in self.suggestions if s['status'] == 'aceito'])
        rejeitados = len([s for s in self.suggestions if s['status'] == 'rejeitado'])
        pendentes = len([s for s in self.suggestions if s['status'] == 'pendente'])
        
        print(f"\n{SuggestionConfig.COLORS['BOLD']}{SuggestionConfig.COLORS['HEADER']}")
        print("=" * 60)
        print("ESTATÍSTICAS DE SUGESTÕES")
        print("=" * 60)
        print(f"{SuggestionConfig.COLORS['ENDC']}")
        
        print(f"Total:      {SuggestionConfig.COLORS['BLUE']}{total}{SuggestionConfig.COLORS['ENDC']}")
        print(f"Aceitos:    {SuggestionConfig.COLORS['GREEN']}✓ {aceitos}{SuggestionConfig.COLORS['ENDC']}")
        print(f"Rejeitados: {SuggestionConfig.COLORS['RED']}✗ {rejeitados}{SuggestionConfig.COLORS['ENDC']}")
        print(f"Pendentes:  {SuggestionConfig.COLORS['YELLOW']}⏳ {pendentes}{SuggestionConfig.COLORS['ENDC']}")
        
        if total > 0:
            taxa_aceito = (aceitos / total) * 100
            print(f"\nTaxa de Aceitação: {taxa_aceito:.1f}%")
        
        # Estatísticas por tipo
        tipos = {}
        for s in self.suggestions:
            t = s['tipo']
            tipos[t] = tipos.get(t, 0) + 1
        
        if tipos:
            print(f"\nPor Tipo:")
            for tipo, count in sorted(tipos.items()):
                icone, nome = SuggestionConfig.CATEGORIES.get(tipo, ('💡', tipo))
                print(f"  {icone} {nome}: {count}")
        
        print(f"\n{SuggestionConfig.COLORS['BOLD']}{'=' * 60}{SuggestionConfig.COLORS['ENDC']}\n")
    
    def mostrar_historico(self) -> None:
        """Mostra histórico de decisões"""
        
        if not self.history:
            print(f"{SuggestionConfig.COLORS['YELLOW']}ℹ Nenhum histórico{SuggestionConfig.COLORS['ENDC']}")
            return
        
        print(f"\n{SuggestionConfig.COLORS['BOLD']}{SuggestionConfig.COLORS['HEADER']}")
        print("=" * 80)
        print("HISTÓRICO DE DECISÕES (últimas 10)")
        print("=" * 80)
        print(f"{SuggestionConfig.COLORS['ENDC']}\n")
        
        for item in self.history[-10:]:
            acao_cor = SuggestionConfig.COLORS['GREEN'] if item['acao'] == 'aceito' else SuggestionConfig.COLORS['RED']
            acao_icon = '✓' if item['acao'] == 'aceito' else '✗'
            
            print(f"{acao_cor}{acao_icon} {item['acao'].upper()}{SuggestionConfig.COLORS['ENDC']} | "
                  f"ID: {item['id']:3d} | {item['arquivo']:30s} | {item['timestamp']}")
        
        print(f"\n{SuggestionConfig.COLORS['BOLD']}{'=' * 80}{SuggestionConfig.COLORS['ENDC']}\n")
    
    # ========================================================================
    # MENU INTERATIVO
    # ========================================================================
    
    def menu_principal(self) -> None:
        """Menu interativo principal"""
        
        while True:
            print(f"\n{SuggestionConfig.COLORS['BOLD']}{SuggestionConfig.COLORS['HEADER']}")
            print("╔" + "═" * 58 + "╗")
            print("║" + " GERENCIADOR DE SUGESTÕES - WINDSURF INTEGRATION ".center(58) + "║")
            print("╚" + "═" * 58 + "╝")
            print(f"{SuggestionConfig.COLORS['ENDC']}")
            
            print("\n1. Revisar sugestões")
            print("2. Listar pendentes")
            print("3. Estatísticas")
            print("4. Histórico")
            print("5. Sair")
            
            opcao = input(f"\n{SuggestionConfig.COLORS['BOLD']}Escolha uma opção > {SuggestionConfig.COLORS['ENDC']}").strip()
            
            if opcao == '1':
                self.revisar_sugestoes()
            elif opcao == '2':
                self.listar_pendentes()
            elif opcao == '3':
                self.mostrar_estatisticas()
            elif opcao == '4':
                self.mostrar_historico()
            elif opcao == '5':
                print(f"\n{SuggestionConfig.COLORS['GREEN']}✓ Até logo!{SuggestionConfig.COLORS['ENDC']}\n")
                break
            else:
                print(f"{SuggestionConfig.COLORS['RED']}✗ Opção inválida{SuggestionConfig.COLORS['ENDC']}")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    
    manager = SuggestionManager()
    
    # Parse arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--review':
            manager.revisar_sugestoes()
        elif sys.argv[1] == '--history':
            manager.mostrar_historico()
        elif sys.argv[1] == '--stats':
            manager.mostrar_estatisticas()
        else:
            print("Uso: python suggestion_manager.py [--review|--history|--stats]")
    else:
        # Menu interativo
        manager.menu_principal()
