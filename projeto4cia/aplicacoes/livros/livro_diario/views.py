import json
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from aplicacoes.cadastros.cadastro_comandante.models import Comandante
from aplicacoes.cadastros.cadastro_policiais.models import Policial
from aplicacoes.cadastros.cadastro_vtrs.models import Viatura
from .models import LivroDiarioRelatorio

@login_required
def livro_diario(request):
    hoje = timezone.localdate()
    
    context = {
        'usuario_logado': request.user,
        'policial_logado': getattr(request.user, 'policial', None),
        'comandante': Comandante.objects.order_by('-data_nomeacao').first(),
        'data_anterior': (hoje - timedelta(days=1)).strftime('%d/%m/%Y'),
        'data_hoje': hoje.strftime('%d/%m/%Y'),
        'policiais': Policial.objects.filter(ativo=True),
        'viaturas': Viatura.objects.filter(ativo=True).order_by('prefixo'),
    }
    return render(request, 'livro_diario/livro_diario.html', context)

@login_required
def gerar_relatorio(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Método não permitido'}, status=405)
    
    try:
        # Mapeamentos para tradução de valores
        MAP_TURNOS = {
            '1o_GIRO': '1º GIRO',
            '2o_GIRO': '2º GIRO',
            '1o_QTU': '1º QTU',
            '2o_QTU': '2º QTU',
            '24HS': '24HS',
            '06H': '06H',
        }

        MAP_FUNCOES = {
            'cmt_da_vtr_mike': 'CMT DA VTR/MIKE',
            'motorista': 'MOTORISTA',
            'patrulheiro': 'PATRULHEIRO',
            'motociclista': 'MOTOCICLISTA',
            'atendente': 'APOIO POLICIAL',
            'outros': 'OUTROS',
        }

        MAP_MOTIVOS = {
            'folga': 'FOLGA',
            'licenca_saude': 'LICENÇA SAÚDE',
            'luto': 'LUTO',
            'casamento': 'CASAMENTO',
            'treinamento': 'TREINAMENTO',
            'servico_admin': 'SERVIÇO ADMINISTRATIVO',
            'dispensado_cmd': 'DISPENSADO PELO CMD DA CIA',
            'arma_fogo': 'DISPENSADO POR ARMA DE FOGO',
            'reforco_policial': 'DISPENSADO POR REFORÇO POLICIAL',
            'outros': 'OUTROS',
        }

        MAP_PROBLEMAS_VTR = {
            'sem_problema': 'SEM PROBLEMA',
            'motor_nao_liga': 'Motor não liga',
            'motor_falhando': 'Motor falhando',
            'motor_batendo': 'Motor batendo',
            'motor_superaquecendo': 'Motor superaquecendo',
            'bateria_descarregada': 'Bateria descarregada',
            'sirene_sem_funcionar': 'Sirene sem funcionar',
            'giroflex_sem_funcionar': 'Giroflex sem funcionar',
            'pneu_furado': 'Pneu furado',
            'pneu_murcho': 'Pneu murcho',
            'vazamento_nao_identificado': 'Vazamento não identificado',
            'indisponivel_para_servico': 'Indisponível para serviço',
        }

        MAP_DOCUMENTOS = {
            'oficio': 'Ofício',
            'memorando': 'Memorando',
            'circular': 'Circular',
            'boletim_interno': 'Boletim interno',
            'requerimento': 'Requerimento',
            'atestado_medico': 'Atestado médico',
            'escala_servico': 'Escala de serviço',
            'boletim_ocorrencia': 'Boletim de ocorrência',
            'parte_diaria': 'Parte diária',
            'outro': 'Outro',
        }

        def traduzir(valor, mapa, default=''):
            if not valor:
                return default
            return mapa.get(valor, valor)

        # Processa todos os campos do POST
        form_data = {}
        
        for key in request.POST.keys():
            if key.endswith('[]'):
                values = request.POST.getlist(key)
                clean_key = key.rstrip('[]')
                form_data[clean_key] = [v for v in values if v]
            else:
                form_data[key] = request.POST.get(key)
        
        # ==================== 1. PERMANÊNCIA ====================
        permanencias = []
        permanencia_list = form_data.get('permanencia', [])
        permuta_list = form_data.get('permuta_permanencia', [])
        servico_list = form_data.get('servico_permanencia', [])
        
        max_len = max(len(permanencia_list), len(permuta_list), len(servico_list))
        
        for i in range(max_len):
            policial_id = permanencia_list[i] if i < len(permanencia_list) else None
            permuta_id = permuta_list[i] if i < len(permuta_list) else None
            servico = servico_list[i] if i < len(servico_list) else None
            
            policial_nome = ""
            if policial_id:
                try:
                    policial = Policial.objects.get(id=policial_id)
                    policial_nome = f"{policial.get_patente_display()} {policial.numero_barra}/{policial.barra} {policial.nome_guerra}"
                except:
                    policial_nome = policial_id
            
            permuta_nome = ""
            if permuta_id and permuta_id != "sem_permuta":
                try:
                    permuta = Policial.objects.get(id=permuta_id)
                    permuta_nome = f"{permuta.get_patente_display()} {permuta.numero_barra}/{permuta.barra} {permuta.nome_guerra}"
                except:
                    permuta_nome = permuta_id
            elif permuta_id == "sem_permuta":
                permuta_nome = "SEM PERMUTA"
            
            if policial_id:
                permanencias.append({
                    'policial': policial_nome,
                    'permuta': permuta_nome,
                    'servico': traduzir(servico, MAP_TURNOS, servico)
                })
        form_data['permanencias_lista'] = permanencias
        
        # ==================== 2. SERVIÇO EXTERNO ====================
        servicos_externos = []
        policial_externo_list = form_data.get('policial_externo', [])
        permuta_externo_list = form_data.get('permuta_externo', [])
        hora_externo_list = form_data.get('hora_externo', [])
        vtr_servico_list = form_data.get('vtr_servico', [])
        funcao_externo_list = form_data.get('funcao_externo', [])

        for i in range(len(policial_externo_list)):
            policial_id = policial_externo_list[i]
            if policial_id:
                try:
                    policial = Policial.objects.get(id=policial_id)
                    policial_nome = f"{policial.get_patente_display()} {policial.numero_barra}/{policial.barra} {policial.nome_guerra}"
                except:
                    policial_nome = policial_id
                
                # CORREÇÃO AQUI: Buscar o nome do policial da permuta
                permuta_nome = "SEM PERMUTA"
                permuta_id = permuta_externo_list[i] if i < len(permuta_externo_list) else ""
                
                if permuta_id and permuta_id not in ['', 'sem_permuta', 'SEM PERMUTA']:
                    try:
                        permuta = Policial.objects.get(id=permuta_id)
                        permuta_nome = f"{permuta.get_patente_display()} {permuta.numero_barra}/{permuta.barra} {permuta.nome_guerra}"
                    except:
                        permuta_nome = permuta_id
                elif permuta_id == "sem_permuta":
                    permuta_nome = "SEM PERMUTA"
                
                vtr_nome = vtr_servico_list[i] if i < len(vtr_servico_list) else ""
                if vtr_nome:
                    try:
                        viatura = Viatura.objects.get(id=vtr_nome)
                        vtr_nome = f"{viatura.prefixo} - {viatura.modelo}"
                    except:
                        pass
                
                servicos_externos.append({
                    'policial': policial_nome,
                    'permuta': permuta_nome,  # AGORA USA O NOME BUSCADO
                    'hora': traduzir(hora_externo_list[i] if i < len(hora_externo_list) else "", MAP_TURNOS),
                    'vtr': vtr_nome,
                    'funcao': traduzir(funcao_externo_list[i] if i < len(funcao_externo_list) else "", MAP_FUNCOES)
                })
        form_data['servicos_externos_lista'] = servicos_externos
        
        # ==================== 3. REMANEJAMENTO ====================
        remanejamentos = []
        policial_remanejamento_list = form_data.get('policial_remanejamento', [])
        posto_escalado_list = form_data.get('posto_escalado', [])
        posto_remanejado_list = form_data.get('posto_remanejado', [])
        
        for i in range(len(policial_remanejamento_list)):
            policial_id = policial_remanejamento_list[i]
            if policial_id:
                try:
                    policial = Policial.objects.get(id=policial_id)
                    policial_nome = f"{policial.get_patente_display()} {policial.numero_barra}/{policial.barra} {policial.nome_guerra}"
                except:
                    policial_nome = policial_id
                
                posto_escalado_nome = posto_escalado_list[i] if i < len(posto_escalado_list) else ""
                if posto_escalado_nome and posto_escalado_nome != "sem_permuta":
                    try:
                        posto = Policial.objects.get(id=posto_escalado_nome)
                        posto_escalado_nome = f"{posto.get_patente_display()} {posto.numero_barra}/{posto.barra} {posto.nome_guerra}"
                    except:
                        pass
                
                remanejamentos.append({
                    'policial': policial_nome,
                    'posto_escalado': posto_escalado_nome if posto_escalado_nome else "SEM PERMUTA",
                    'posto_remanejado': traduzir(posto_remanejado_list[i] if i < len(posto_remanejado_list) else "", MAP_FUNCOES)
                })
        form_data['remanejamentos_lista'] = remanejamentos
        
        # ==================== 4. DISPENSAS ====================
        dispensas = []
        policial_dispensa_list = form_data.get('policial_dispensa', [])
        turno_dispensa_list = form_data.get('turno_hora_dispensa', [])
        motivo_dispensa_list = form_data.get('motivo_dispensa', [])
        observacao_dispensa_list = form_data.get('observacao_dispensa', [])
        
        for i in range(len(policial_dispensa_list)):
            policial_id = policial_dispensa_list[i]
            if policial_id:
                try:
                    policial = Policial.objects.get(id=policial_id)
                    policial_nome = f"{policial.get_patente_display()} {policial.numero_barra}/{policial.barra} {policial.nome_guerra}"
                except:
                    policial_nome = policial_id
                
                dispensas.append({
                    'policial': policial_nome,
                    'turno': traduzir(turno_dispensa_list[i] if i < len(turno_dispensa_list) else "", MAP_TURNOS),
                    'motivo': traduzir(motivo_dispensa_list[i] if i < len(motivo_dispensa_list) else "", MAP_MOTIVOS),
                    'observacao': observacao_dispensa_list[i] if i < len(observacao_dispensa_list) else ""
                })
        form_data['dispensas_lista'] = dispensas
        
        # ==================== 5. FALTAS ====================
        faltas = []
        policial_falta_list = form_data.get('policial_falta', [])
        turno_falta_list = form_data.get('turno_hora_falta', [])
        motivo_falta_list = form_data.get('motivo_falta', [])
        observacao_falta_list = form_data.get('observacao_falta', [])
        
        for i in range(len(policial_falta_list)):
            policial_id = policial_falta_list[i]
            if policial_id:
                try:
                    policial = Policial.objects.get(id=policial_id)
                    policial_nome = f"{policial.get_patente_display()} {policial.numero_barra}/{policial.barra} {policial.nome_guerra}"
                except:
                    policial_nome = policial_id
                
                faltas.append({
                    'policial': policial_nome,
                    'turno': traduzir(turno_falta_list[i] if i < len(turno_falta_list) else "", MAP_TURNOS),
                    'motivo': traduzir(motivo_falta_list[i] if i < len(motivo_falta_list) else "", MAP_MOTIVOS),
                    'observacao': observacao_falta_list[i] if i < len(observacao_falta_list) else ""
                })
        form_data['faltas_lista'] = faltas
        
        # ==================== 6. BAIXAS ====================
        baixas = []
        policial_baixa_list = form_data.get('policial_baixa', [])
        turno_baixa_list = form_data.get('turno_hora_baixa', [])
        motivo_baixa_list = form_data.get('motivo_baixa', [])
        observacao_baixa_list = form_data.get('observacao_baixa', [])
        
        for i in range(len(policial_baixa_list)):
            policial_id = policial_baixa_list[i]
            if policial_id:
                try:
                    policial = Policial.objects.get(id=policial_id)
                    policial_nome = f"{policial.get_patente_display()} {policial.numero_barra}/{policial.barra} {policial.nome_guerra}"
                except:
                    policial_nome = policial_id
                
                baixas.append({
                    'policial': policial_nome,
                    'turno': traduzir(turno_baixa_list[i] if i < len(turno_baixa_list) else "", MAP_TURNOS),
                    'motivo': traduzir(motivo_baixa_list[i] if i < len(motivo_baixa_list) else "", MAP_MOTIVOS),
                    'observacao': observacao_baixa_list[i] if i < len(observacao_baixa_list) else ""
                })
        form_data['baixas_lista'] = baixas
        
        # ==================== 7. LIBERAÇÕES ====================
        liberacoes = []
        policial_liberacao_list = form_data.get('policial_liberacao', [])
        turno_liberacao_list = form_data.get('turno_hora_liberacao', [])
        motivo_liberacao_list = form_data.get('motivo_liberacao', [])
        observacao_liberacao_list = form_data.get('observacao_liberacao', [])
        
        for i in range(len(policial_liberacao_list)):
            policial_id = policial_liberacao_list[i]
            if policial_id:
                try:
                    policial = Policial.objects.get(id=policial_id)
                    policial_nome = f"{policial.get_patente_display()} {policial.numero_barra}/{policial.barra} {policial.nome_guerra}"
                except:
                    policial_nome = policial_id
                
                liberacoes.append({
                    'policial': policial_nome,
                    'turno': traduzir(turno_liberacao_list[i] if i < len(turno_liberacao_list) else "", MAP_TURNOS),
                    'motivo': traduzir(motivo_liberacao_list[i] if i < len(motivo_liberacao_list) else "", MAP_MOTIVOS),
                    'observacao': observacao_liberacao_list[i] if i < len(observacao_liberacao_list) else ""
                })
        form_data['liberacoes_lista'] = liberacoes
        
        # ==================== 8. ATRASOS ====================
        atrasos = []
        policial_atraso_list = form_data.get('policial_atraso', [])
        observacao_atraso_list = form_data.get('observacao_atraso', [])
        
        for i in range(len(policial_atraso_list)):
            policial_id = policial_atraso_list[i]
            if policial_id:
                try:
                    policial = Policial.objects.get(id=policial_id)
                    policial_nome = f"{policial.get_patente_display()} {policial.numero_barra}/{policial.barra} {policial.nome_guerra}"
                except:
                    policial_nome = policial_id
                
                atrasos.append({
                    'policial': policial_nome,
                    'observacao': observacao_atraso_list[i] if i < len(observacao_atraso_list) else ""
                })
        form_data['atrasos_lista'] = atrasos
        
        # ==================== 9. VIATURAS ====================
        viaturas = []
        vtr_servico_vtr_list = form_data.get('vtr_servico', [])
        hora_vtr_list = form_data.get('hora_vtr', [])
        motorista_vtr_list = form_data.get('motorista_vtr', [])
        problema_vtr_list = form_data.get('problema_vtr', [])
        
        for i in range(len(vtr_servico_vtr_list)):
            vtr_id = vtr_servico_vtr_list[i]
            if vtr_id:
                try:
                    viatura = Viatura.objects.get(id=vtr_id)
                    vtr_nome = f"{viatura.prefixo} - {viatura.modelo}"
                except:
                    vtr_nome = vtr_id
                
                motorista_nome = ""
                motorista_id = motorista_vtr_list[i] if i < len(motorista_vtr_list) else ""
                if motorista_id:
                    try:
                        motorista = Policial.objects.get(id=motorista_id)
                        motorista_nome = f"{motorista.get_patente_display()} {motorista.numero_barra}/{motorista.barra} {motorista.nome_guerra}"
                    except:
                        motorista_nome = motorista_id
                
                viaturas.append({
                    'vtr': vtr_nome,
                    'turno': traduzir(hora_vtr_list[i] if i < len(hora_vtr_list) else "", MAP_TURNOS),
                    'motorista': motorista_nome,
                    'problema': traduzir(problema_vtr_list[i] if i < len(problema_vtr_list) else "sem_problema", MAP_PROBLEMAS_VTR)
                })
        form_data['viaturas_lista'] = viaturas
        
        # ==================== 10. BOLETINS DE OCORRÊNCIA ====================
        boletins = []
        bo_numero_list = form_data.get('bo_numero', [])
        bo_tipo_list = form_data.get('bo_tipo_criminal', [])
        
        for i in range(len(bo_numero_list)):
            if bo_numero_list[i]:
                boletins.append({
                    'numero': bo_numero_list[i],
                    'tipo': bo_tipo_list[i] if i < len(bo_tipo_list) else ""
                })
        form_data['boletins_lista'] = boletins
        
        # ==================== 11. OCORRÊNCIAS DE TRÂNSITO ====================
        transitos = []
        ait_list = form_data.get('ocorrencia_ait', [])
        tcacp_list = form_data.get('ocorrencia_tcacp', [])
        frv_list = form_data.get('ocorrencia_frv', [])
        arv_list = form_data.get('ocorrencia_arv', [])
        cnh_list = form_data.get('ocorrencia_cnh', [])
        crlv_list = form_data.get('ocorrencia_crlv', [])
        
        for i in range(len(ait_list)):
            if ait_list[i] or tcacp_list[i] or frv_list[i]:
                transitos.append({
                    'ait': ait_list[i] if i < len(ait_list) else "",
                    'tcacp': tcacp_list[i] if i < len(tcacp_list) else "",
                    'frv': frv_list[i] if i < len(frv_list) else "",
                    'arv': arv_list[i] if i < len(arv_list) else "",
                    'cnh': cnh_list[i] if i < len(cnh_list) else "",
                    'crlv': crlv_list[i] if i < len(crlv_list) else ""
                })
        form_data['transitos_lista'] = transitos
        
        # ==================== 12. ABASTECIMENTOS ====================
        abastecimentos = []
        viatura_km_litros_list = form_data.get('viatura_km_litros', [])
        km_viatura_list = form_data.get('km_viatura', [])
        quantidade_litros_list = form_data.get('quantidade_litros', [])
        
        for i in range(len(viatura_km_litros_list)):
            vtr_id = viatura_km_litros_list[i]
            if vtr_id:
                try:
                    viatura = Viatura.objects.get(id=vtr_id)
                    vtr_nome = f"{viatura.prefixo} - {viatura.modelo}"
                except:
                    vtr_nome = vtr_id
                
                abastecimentos.append({
                    'viatura': vtr_nome,
                    'km': km_viatura_list[i] if i < len(km_viatura_list) else "",
                    'litros': quantidade_litros_list[i] if i < len(quantidade_litros_list) else ""
                })
        form_data['abastecimentos_lista'] = abastecimentos
        
        # ==================== 13. INSTALAÇÕES ====================
        instalacoes = []
        observacoes_instalacoes_list = form_data.get('observacoes_instalacoes', [])
        
        for obs in observacoes_instalacoes_list:
            if obs:
                instalacoes.append({'observacao': obs})
        form_data['instalacoes_lista'] = instalacoes
        
        # ==================== 14. DOCUMENTAÇÃO ====================
        documentos = []
        documento_nome_list = form_data.get('documento_nome', [])
        observacoes_documentacao_list = form_data.get('observacoes_documentacao', [])
        
        for i in range(len(documento_nome_list)):
            if documento_nome_list[i]:
                documentos.append({
                    'documento': traduzir(documento_nome_list[i], MAP_DOCUMENTOS),
                    'observacao': observacoes_documentacao_list[i] if i < len(observacoes_documentacao_list) else ""
                })
        form_data['documentos_lista'] = documentos
        
        # ==================== 15. ASSUNTOS GERAIS ====================
        assuntos = []
        assunto_texto_list = form_data.get('assunto_texto', [])
        
        for assunto in assunto_texto_list:
            if assunto:
                assuntos.append({'assunto': assunto})
        form_data['assuntos_lista'] = assuntos
        
        # ==================== 16. CRIME COMUM ====================
        crime_comum_obs = []
        observacoes_crime_comum_list = form_data.get('observacoes_crime_comum', [])
        
        for obs in observacoes_crime_comum_list:
            if obs:
                crime_comum_obs.append({'observacao': obs})
        form_data['crime_comum_lista'] = crime_comum_obs
        
        # ==================== 17. CRIME MILITAR ====================
        crime_militar_obs = []
        observacoes_crime_militar_list = form_data.get('observacoes_crime_militar', [])
        
        for obs in observacoes_crime_militar_list:
            if obs:
                crime_militar_obs.append({'observacao': obs})
        form_data['crime_militar_lista'] = crime_militar_obs
        
        # ==================== 18. ALTERAÇÃO DE OFICIAL ====================
        alteracao_oficial_obs = []
        observacoes_alteracao_oficial_list = form_data.get('observacoes_alteracao_oficial', [])
        
        for obs in observacoes_alteracao_oficial_list:
            if obs:
                alteracao_oficial_obs.append({'observacao': obs})
        form_data['alteracao_oficial_lista'] = alteracao_oficial_obs
        
        # ==================== 19. ALTERAÇÃO DE PRAÇA ====================
        alteracao_praca_obs = []
        observacoes_alteracao_praca_list = form_data.get('observacoes_alteracao_praca', [])
        
        for obs in observacoes_alteracao_praca_list:
            if obs:
                alteracao_praca_obs.append({'observacao': obs})
        form_data['alteracao_praca_lista'] = alteracao_praca_obs
        
        # ==================== 20. ALTERAÇÕES DO SERVIÇO ====================
        alteracoes_servico = []
        obs_alteracoes_servico_list = form_data.get('obs_alteracoes_servico', [])
        
        for obs in obs_alteracoes_servico_list:
            if obs:
                alteracoes_servico.append({'observacao': obs})
        form_data['alteracoes_servico_lista'] = alteracoes_servico
        
        # ==================== 21. POLICIAL SUBSTITUTO ====================
        policial_substituto_id = form_data.get('policial_substituto', '')
        policial_substituto_nome = "NENHUM - PERMANEÇO NO SERVIÇO"
        if policial_substituto_id and policial_substituto_id not in ['', 'sem_permuta', 'NENHUM - PERMANEÇO NO SERVIÇO']:
            try:
                substituto = Policial.objects.get(id=policial_substituto_id)
                policial_substituto_nome = f"{substituto.get_patente_display()} {substituto.numero_barra}/{substituto.barra} {substituto.nome_guerra}"
            except:
                pass
        form_data['policial_substituto_nome'] = policial_substituto_nome
        
        # ==================== DADOS ADICIONAIS ====================
        comandante_obj = Comandante.objects.filter(ativo=True).order_by('-data_nomeacao').first()
        comandante_nome = ""
        if comandante_obj:
            comandante_nome = f"{comandante_obj.get_patente_display()} {comandante_obj.nome_guerra}"
        
        policial_logado_obj = getattr(request.user, 'policial', None)
        
        # Adicionar data_anterior e data_hoje ao form_data para o template
        form_data['data_anterior'] = (timezone.localdate() - timedelta(days=1)).strftime('%d/%m/%Y')
        form_data['data_hoje'] = timezone.localdate().strftime('%d/%m/%Y')
        
        context = {
            'dados': form_data,
            'usuario': request.user,
            'policial_logado': policial_logado_obj,
            'comandante': comandante_obj,
            'comandante_nome': comandante_nome,
            'data_geracao': timezone.localtime().strftime('%d/%m/%Y %H:%M:%S'),
            'data_anterior': (timezone.localdate() - timedelta(days=1)).strftime('%d/%m/%Y'),
            'data_hoje': timezone.localdate().strftime('%d/%m/%Y'),
        }
        
        html_content = render_to_string('livro_diario/relatorio_imutavel.html', context)
        
        relatorio = LivroDiarioRelatorio.objects.create(
            usuario=request.user,
            data_escala=timezone.localdate(),
            conteudo_html=html_content
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Relatório gerado com sucesso',
            'redirect_url': reverse('livro_diario:visualizar_relatorio', args=[relatorio.id])
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def visualizar_relatorio(request, relatorio_id):
    relatorio = get_object_or_404(LivroDiarioRelatorio, id=relatorio_id)
    
    if not (request.user.is_superuser or relatorio.usuario == request.user):
        return HttpResponse('Sem permissão', status=403)
    
    return HttpResponse(relatorio.conteudo_html)

@login_required
def listar_relatorios(request):
    # Verifica se é uma requisição AJAX (para manter compatibilidade)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.user.is_superuser:
            relatorios = LivroDiarioRelatorio.objects.all()[:50]
        else:
            relatorios = LivroDiarioRelatorio.objects.filter(usuario=request.user)[:50]
        
        dados = [{
            'id': r.id,
            'data': r.data_criacao.strftime('%d/%m/%Y %H:%M'),
            'data_escala': r.data_escala.strftime('%d/%m/%Y'),
        } for r in relatorios]
        
        return JsonResponse({'relatorios': dados})
    
    # Se não for AJAX, renderiza o template HTML
    return render(request, 'livro_diario/listar_relatorios.html')

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

@csrf_exempt
@require_POST
def gerar_relatorio_whatsapp(request):
    """Gera um relatório formatado para WhatsApp"""
    try:
        data = json.loads(request.body.decode('utf-8'))
        dados = data.get('dados', {})
        
        # Construir mensagem para WhatsApp
        mensagem = []
        
        # Cabeçalho
        mensagem.append("🏛️ *POLÍCIA MILITAR DO MARANHÃO*")
        mensagem.append("🏢 *4ª CIA/11º BPM - MATÕES*")
        mensagem.append("")
        mensagem.append("📋 *LIVRO DIÁRIO DE SERVIÇO*")
        mensagem.append("")
        mensagem.append("=" * 40)
        mensagem.append("")
        
        # Parte Diária - pegar o nome do policial logado
        policial_nome = ""
        if hasattr(request.user, 'policial') and request.user.policial:
            policial_nome = f"{request.user.policial.get_patente_display()} {request.user.policial.nome_guerra}"
        else:
            policial_nome = request.user.get_full_name() or request.user.username or "NÃO IDENTIFICADO"
        
        mensagem.append(f"👮 *PARTE DIÁRIA*")
        mensagem.append(f"Oficial: {policial_nome}")
        mensagem.append(f"Período: {dados.get('data_anterior', 'N/A')} → {dados.get('data_hoje', 'N/A')}")
        mensagem.append(f"Comandante: {dados.get('comandante_nome', 'N/A')}")
        mensagem.append("")
        
        # Serviço Interno
        mensagem.append("=" * 40)
        mensagem.append("📌 *1. SERVIÇO INTERNO*")
        mensagem.append("")
        
        # Permanência
        permanencia = dados.get('permanencia', [])
        if permanencia and permanencia[0]:
            mensagem.append("🔹 *PERMANÊNCIA:*")
            for p in permanencia:
                if p:
                    mensagem.append(f"   • {p}")
        else:
            mensagem.append("🔹 *PERMANÊNCIA:* Sem registro")
        
        # Serviço Externo
        if dados.get('policial_externo'):
            mensagem.append("")
            mensagem.append("🔹 *SERVIÇO EXTERNO:*")
            mensagem.append(f"   • Policial: {dados.get('policial_externo')}")
            if dados.get('permuta_externo'):
                mensagem.append(f"   • Permuta: {dados.get('permuta_externo')}")
            mensagem.append(f"   • VTR: {dados.get('vtr_servico', 'N/A')}")
        
        mensagem.append("")
        
        # Alterações
        mensagem.append("=" * 40)
        mensagem.append("🔄 *ALTERAÇÕES DO SERVIÇO*")
        mensagem.append("")
        
        alteracoes = []
        if dados.get('remanejamento_alteracao') == 'com_alteracao':
            alteracoes.append("✅ Remanejamento realizado")
        if dados.get('dispensa_alteracao') == 'com_alteracao':
            policial_dispensa = dados.get('policial_dispensa', '')
            motivo = dados.get('motivo_dispensa', '')
            alteracoes.append(f"✅ Dispensa: {policial_dispensa} - {motivo}")
        if dados.get('falta_alteracao') == 'com_alteracao':
            alteracoes.append("✅ Registro de falta")
        if dados.get('baixa_alteracao') == 'com_alteracao':
            alteracoes.append("✅ Registro de baixa")
        if dados.get('viatura_alteracao') == 'com_alteracao':
            alteracoes.append("✅ Alteração na VTR")
        
        if alteracoes:
            for alt in alteracoes:
                mensagem.append(f"   • {alt}")
        else:
            mensagem.append("   • SEM ALTERAÇÕES")
        
        mensagem.append("")
        
        # Ensino e Instrução
        mensagem.append("=" * 40)
        mensagem.append("📚 *2. ENSINO E INSTRUÇÃO*")
        mensagem.append("")
        
        if dados.get('ensino_alteracao') == 'com_alteracao':
            ensino_obs = dados.get('ensino_observacoes', 'Com alteração')
            mensagem.append(f"   • Ensino: {ensino_obs}")
        else:
            mensagem.append("   • Ensino: SEM ALTERAÇÃO")
        
        if dados.get('instrucao_alteracao') == 'com_alteracao':
            instrucao_obs = dados.get('instrucao_observacoes', 'Com alteração')
            mensagem.append(f"   • Instrução: {instrucao_obs}")
        else:
            mensagem.append("   • Instrução: SEM ALTERAÇÃO")
        
        mensagem.append("")
        
        # Assuntos Gerais
        mensagem.append("=" * 40)
        mensagem.append("📄 *3. ASSUNTOS GERAIS*")
        mensagem.append("")
        
        has_assuntos = False
        if dados.get('km_litros_alteracao') == 'com_alteracao':
            mensagem.append("   • ⛽ Abastecimento realizado")
            has_assuntos = True
        if dados.get('instalacoes_alteracao') == 'com_alteracao':
            mensagem.append("   • 🔧 Alteração nas instalações")
            has_assuntos = True
        if dados.get('documentacao_alteracao') == 'com_alteracao':
            mensagem.append("   • 📄 Documentação recebida")
            has_assuntos = True
        if not has_assuntos:
            mensagem.append("   • SEM ALTERAÇÕES")
        
        mensagem.append("")
        
        # Justiça e Disciplina
        mensagem.append("=" * 40)
        mensagem.append("⚖️ *4. JUSTIÇA E DISCIPLINA*")
        mensagem.append("")
        
        has_justica = False
        if dados.get('crime_comum_alteracao') == 'com_alteracao':
            mensagem.append("   • ⚠️ Registro de Crime Comum")
            has_justica = True
        if dados.get('crime_militar_alteracao') == 'com_alteracao':
            mensagem.append("   • ⚠️ Registro de Crime Militar")
            has_justica = True
        if not has_justica:
            mensagem.append("   • Nenhum registro")
        
        mensagem.append("")
        
        # Passagem de Serviço
        mensagem.append("=" * 40)
        mensagem.append("🔄 *5. PASSAGEM DE SERVIÇO*")
        mensagem.append("")
        texto_passagem = dados.get('texto_passagem', 'PERMANEÇO NO SERVIÇO DE 24 HORAS')
        mensagem.append(f"📝 {texto_passagem}")
        
        mensagem.append("")
        mensagem.append("=" * 40)
        mensagem.append("")
        mensagem.append(f"📅 Matões-MA, {dados.get('data_hoje', 'N/A')}")
        mensagem.append("")
        mensagem.append(f"👮 *Assinatura:* {policial_nome}")
        mensagem.append("")
        mensagem.append("---")
        mensagem.append("📱 *Relatório gerado automaticamente pelo sistema*")
        
        # Unir mensagem
        texto_mensagem = "\n".join(mensagem)
        
        return JsonResponse({
            'success': True,
            'mensagem': texto_mensagem
        })
        
    except Exception as e:
        print(f"Erro ao gerar relatório WhatsApp: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'success': False,
            'message': f'Erro: {str(e)}'
        }, status=500)