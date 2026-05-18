import streamlit as st
import pandas as pd
import ollama
from io import BytesIO
from pathlib import Path
import concurrent.futures

# ==========================================
# Internationalization (i18n) Master Dictionary
# ==========================================
I18N = {
    "English": {
        "title": "📚 Teacher Coach AI",
        "subtitle": "Offline educational assistant powered by Gemma for rural and low-resource schools.",
        "badge_offline": "📴 Local · Low Cost · Offline Ready",
        "welcome_title": "## Welcome, teacher",
        "welcome_desc": "Analyze student grades, identify learning gaps, and receive practical recommendations to improve classroom performance, even in places with limited internet access.",
        "bullet_points": "- 📊 Student performance analysis\n- 🤖 Gemma AI recommendations\n- 🧭 Curriculum alignment\n- 👩‍🏫 Personalized support per student",
        "login_card_title": "### Teacher Login",
        "lbl_username": "Username",
        "lbl_password": "Password",
        "btn_login": "Login",
        "btn_logout": "Logout",
        "err_login": "Incorrect username or password. Use admin/admin.",
        "setup_badge": "🤖 AI Analysis Setup",
        "tab_teacher": "Teacher Upload",
        "tab_admin": "Admin Curriculum",
        "admin_title": "## Admin Curriculum Configuration",
        "admin_desc": "Upload MEDUCA content, national curriculum, school director guidelines, or the teacher's base lesson plan. This becomes the minimum educational framework Gemma must follow.",
        "lbl_curr_source": "Curriculum source",
        "lbl_grade": "Grade level",
        "lbl_subject": "Subject",
        "lbl_browse_curr": "Browse curriculum framework file (Excel/CSV/PDF/Docx)",
        "lbl_align_inst": "Curriculum alignment instructions",
        "curr_saved": "Curriculum saved successfully.",
        "curr_err": "Error reading curriculum file:",
        "file_saved": "File saved locally at:",
        "curr_preview": "### Curriculum Preview",
        "curr_cols": "**Curriculum Columns:** ",
        "map_curr_title": "### Map Curriculum Columns",
        "lbl_col_for": "Column for",
        "map_success": "Curriculum mapping applied successfully.",
        "map_err": "Error applying mapping:",
        "curr_config_alert": "Curriculum configuration will guide Gemma recommendations.",
        "btn_back_upload": "✅ Back to Teacher Upload",
        "upload_title": "## Upload Student Performance Data",
        "upload_desc": "Upload an Excel or CSV file with student grades, attendance, subjects, topics, and competencies.",
        "btn_download_template": "Download Excel Template",
        "lbl_browse_student": "Browse student Excel or CSV file",
        "lbl_teacher_inst": "Additional teacher instructions for Gemma",
        "val_teacher_inst": "Focus on students with low attendance and low scores. Recommend simple activities that do not require internet or expensive materials.",
        "student_uploaded_success": "Student data file uploaded successfully.",
        "map_student_title": "### Map Student File Columns",
        "btn_apply_student_map": "Apply Student Mapping",
        "missing_cols_err": "Missing required columns after mapping: ",
        "student_map_success": "Mapping applied and data loaded successfully.",
        "student_map_err": "Error applying student mapping:",
        "no_file_info": "No file uploaded yet. The app will use sample student data for the demo.",
        "model_time_info": "Recommendation generation with the selected model may take several seconds per student.",
        "no_curr_warn": "⚠️ No attached curriculum found (admin_curriculum_example.csv).",
        "no_curr_info": "An evaluation without a curriculum will be performed, limiting recommendations to general best practices.",
        "chk_understand": "I understand, continue without a personalized curriculum",
        "btn_go_curr": "❌ Go to configure curriculum",
        "btn_analyze_gaps": "Analyze gaps with AI",
        "err_missing_pre_analysis": "Missing required columns before analysis: ",
        "err_ollama_gen": "An error occurred during Ollama recommendation generation. Please check model availability.",
        "err_gen_rec_outer": "Error generating recommendations: ",
        "insights_badge": "✨ AI Insights",
        "dash_title": "## Teacher Analytics Dashboard",
        "metric_students": "Students analyzed",
        "metric_avg": "Class average",
        "metric_at_risk": "Students needing support",
        "metric_weakest": "Weakest subject",
        "chart_title": "## Weak Learning Areas by Subject",
        "rec_per_student_title": "## Recommendations per Student",
        "card_ai_rec": "<h3>🤖 AI Recommendations</h3><div class='recommendation'>Use visual examples and classroom objects for weak topics.</div><div class='recommendation'>Create small support groups for students with similar learning gaps.</div><div class='recommendation'>Apply short weekly assessments to measure progress.</div>",
        "card_weekly": "<h3>📅 Weekly Plan</h3><div class='recommendation'><b>Monday:</b> Guided review of weak topics.</div><div class='recommendation'><b>Wednesday:</b> Practice in small groups.</div><div class='recommendation'><b>Friday:</b> Mini assessment and feedback.</div>",
        "card_responsible": "<h3>🧭 Responsible AI</h3><div class='recommendation'>Recommendations are aligned with curriculum guidance.</div><div class='recommendation'>The system avoids labeling students negatively.</div><div class='recommendation'>The teacher remains in control of decisions.</div>",
        "btn_back_index": "Back to Index",
        "prompt_lang": "English",
        "none_select": "-- None --",
        "lbl_applied": "Applied successfully",
        "nav_heading": "🧭 Navigation",
        "nav_diagnostics": "📊 Performance Diagnostics",
        "nav_chat": "💬 Interactive Teacher Coach",
        "chat_welcome": "Hello! I am your local pedagogical coach. How can I help you design classroom strategies or tailored reinforcement exercises today?",
        "chat_placeholder": "Ask your local educational assistant...",
        "chat_badge": "💬 AI Mentorship Chat",
        "lbl_no_models_warn": "⚠️ No local Gemma models detected. Showing submission targets.",
        "lbl_gap_out": "Learning Gap",
        "lbl_act_out": "Reinforcement Activity",
        "lbl_guide_out": "Teacher Guide"
    },
    "Español": {
        "title": "📚 Teacher Coach AI",
        "subtitle": "Asistente educativo offline impulsado por Gemma para escuelas rurales de bajos recursos.",
        "badge_offline": "📴 Local · Bajo Costo · Listo para Modo Offline",
        "welcome_title": "## Bienvenido, docente",
        "welcome_desc": "Analice las calificaciones de los estudiantes, identifique brechas de aprendizaje y reciba recomendaciones prácticas para mejorar el rendimiento en el aula, incluso en lugares sin internet.",
        "bullet_points": "- 📊 Análisis de rendimiento estudiantil\n- 🤖 Recomendaciones de IA con Gemma\n- 🧭 Alineación curricular\n- 👩‍🏫 Apoyo personalizado por estudiante",
        "login_card_title": "### Acceso Docente",
        "lbl_username": "Usuario",
        "lbl_password": "Contraseña",
        "btn_login": "Iniciar Sesión",
        "btn_logout": "Cerrar Sesión",
        "err_login": "Usuario o contraseña incorrectos. Use admin/admin.",
        "setup_badge": "🤖 Configuración de Análisis de IA",
        "tab_teacher": "Carga del Docente",
        "tab_admin": "Currículo Administrador",
        "admin_title": "## Configuración del Currículo Base",
        "admin_desc": "Cargue los contenidos de MEDUCA, currículo nacional, directrices de la escuela o el plan de lecciones base. Este se convierte en el marco educativo mínimo que Gemma debe seguir.",
        "lbl_curr_source": "Fuente del currículo",
        "lbl_grade": "Nivel de grado",
        "lbl_subject": "Materia",
        "lbl_browse_curr": "Buscar archivo de marco curricular (Excel/CSV/PDF/Docx)",
        "lbl_align_inst": "Instrucciones de alineación curricular",
        "curr_saved": "Currículo guardado exitosamente.",
        "curr_err": "Error al leer el archivo de currículo:",
        "file_saved": "Archivo guardado localmente en:",
        "curr_preview": "### Vista Previa del Currículo",
        "curr_cols": "**Columnas del Currículo:** ",
        "map_curr_title": "### Mapear Columnas del Currículo",
        "lbl_col_for": "Columna para",
        "map_success": "Mapeo de currículo aplicado exitosamente.",
        "map_err": "Error al aplicar el mapeo:",
        "curr_config_alert": "La configuración del currículo guiará las recomendaciones de Gemma.",
        "btn_back_upload": "✅ Volver a Carga del Docente",
        "upload_title": "## Cargar Datos de Rendimiento Estudiantil",
        "upload_desc": "Cargue un archivo Excel o CSV con las calificaciones, asistencia, materias, temas y competencias de los estudiantes.",
        "btn_download_template": "Descargar Plantilla de Excel",
        "lbl_browse_student": "Buscar archivo Excel o CSV de estudiantes",
        "lbl_teacher_inst": "Instrucciones adicionales del docente para Gemma",
        "val_teacher_inst": "Enfócate en estudiantes con baja asistencia y bajas calificaciones. Recomienda actividades simples que no requieran internet ni materiales costosos.",
        "student_uploaded_success": "Archivo de datos de estudiantes cargado exitosamente.",
        "map_student_title": "### Mapear Columnas del Archivo de Estudiantes",
        "btn_apply_student_map": "Aplicar Mapeo de Estudiantes",
        "missing_cols_err": "Faltan columnas obligatorias después del mapeo: ",
        "student_map_success": "Mapeo aplicado y datos cargados exitosamente.",
        "student_map_err": "Error al aplicar el mapeo de estudiantes:",
        "no_file_info": "Ningún archivo cargado aún. La aplicación usará datos de muestra para la demostración.",
        "model_time_info": "La generación de recomendaciones con el modelo seleccionado puede demorar varios segundos por estudiante.",
        "no_curr_warn": "⚠️ No se encontró un currículo adjunto (admin_curriculum_example.csv).",
        "no_curr_info": "Se realizará una evaluación sin currículo base, limitando las recomendaciones a buenas prácticas generales.",
        "chk_understand": "Entiendo, continuar sin un currículo personalizado",
        "btn_go_curr": "❌ Ir a configurar currículo",
        "btn_analyze_gaps": "Analizar brechas con IA",
        "err_missing_pre_analysis": "Faltan columnas requeridas antes del análisis: ",
        "err_ollama_gen": "Ocurrió un error durante la generación de recomendaciones en Ollama. Por favor verifique la disponibilidad del modelo.",
        "err_gen_rec_outer": "Error al generar recomendaciones: ",
        "insights_badge": "✨ Análisis de IA",
        "dash_title": "## Panel de Analítica Docente",
        "metric_students": "Estudiantes analizados",
        "metric_avg": "Promedio de la clase",
        "metric_at_risk": "Estudiantes que requieren apoyo",
        "metric_weakest": "Materia más débil",
        "chart_title": "## Áreas de Aprendizaje Débiles por Materia",
        "rec_per_student_title": "## Recomendaciones por Estudiante",
        "card_ai_rec": "<h3>🤖 Recomendaciones de IA</h3><div class='recommendation'>Use ejemplos visuales y objetos del entorno para temas débiles.</div><div class='recommendation'>Cree pequeños grupos de apoyo para estudiantes con brechas similares.</div><div class='recommendation'>Aplique evaluaciones cortas semanales para medir el progreso.</div>",
        "card_weekly": "<h3>📅 Plan Semanal</h3><div class='recommendation'><b>Lunes:</b> Repaso de temas débiles.</div><div class='recommendation'><b>Miércoles:</b> Práctica en grupos pequeños.</div><div class='recommendation'><b>Viernes:</b> Mini evaluación y retroalimentación.</div>",
        "card_responsible": "<h3>🧭 IA Responsable</h3><div class='recommendation'>Las recomendaciones están alineadas con la guía curricular.</div><div class='recommendation'>El sistema evita etiquetar negativamente a los alumnos.</div><div class='recommendation'>El docente mantiene el control de las decisiones.</div>",
        "btn_back_index": "Volver al Inicio",
        "prompt_lang": "Spanish",
        "none_select": "-- Ninguna --",
        "lbl_applied": "Aplicado con éxito",
        "nav_heading": "🧭 Navegación",
        "nav_diagnostics": "📊 Diagnóstico de Rendimiento",
        "nav_chat": "💬 Asesor Pedagógico Interactivo",
        "chat_welcome": "¡Hola! Soy tu asesor pedagógico local. ¿Cómo te puedo ayudar a diseñar estrategias didácticas o ejercicios de reforzamiento hoy?",
        "chat_placeholder": "Pregúntale a tu asistente educativo local...",
        "chat_badge": "💬 Chat de Mentoría de IA",
        "lbl_no_models_warn": "⚠️ No se detectaron modelos Gemma locales. Mostrando objetivos de entrega.",
        "lbl_gap_out": "Brecha de Aprendizaje",
        "lbl_act_out": "Actividad de Refuerzo",
        "lbl_guide_out": "Guía del Docente"
    },
    "Português": {
        "title": "📚 Teacher Coach AI",
        "subtitle": "Assistente educacional offline impulsionado por Gemma para escolas rurais e de poucos recursos.",
        "badge_offline": "📴 Local · Baixo Custo · Pronto para Modo Offline",
        "welcome_title": "## Bem-vindo, professor",
        "welcome_desc": "Analise as notas dos alunos, identifique lacunas de aprendizagem e receba recomendações práticas para melhorar o desempenho escolar, mesmo em locais sem internet.",
        "bullet_points": "- 📊 Análise de desempenho dos alunos\n- 🤖 Recomendações de IA com Gemma\n- 🧭 Alinhamento curricular\n- 👩‍🏫 Apoio personalizado por aluno",
        "login_card_title": "### Acesso do Professor",
        "lbl_username": "Usuário",
        "lbl_password": "Senha",
        "btn_login": "Entrar",
        "btn_logout": "Sair",
        "err_login": "Usuário ou senha incorretos. Use admin/admin.",
        "setup_badge": "🤖 Configuração de Análise de IA",
        "tab_teacher": "Upload do Professor",
        "tab_admin": "Currículo Administrador",
        "admin_title": "## Configuração do Currículo Base",
        "admin_desc": "Faça o upload dos conteúdos curriculares oficiais ou plano de aulas base. Este se torna o modelo educacional mínimo que o Gemma deve seguir.",
        "lbl_curr_source": "Fonte do currículo",
        "lbl_grade": "Nível de escolaridade",
        "lbl_subject": "Matéria",
        "lbl_browse_curr": "Buscar arquivo de marco curricular (Excel/CSV/PDF/Docx)",
        "lbl_align_inst": "Instruções de alinhamento curricular",
        "curr_saved": "Currículo salvo com sucesso.",
        "curr_err": "Erro ao ler o arquivo de currículo:",
        "file_saved": "Arquivo salvo localmente em:",
        "curr_preview": "### Visualização do Currículo",
        "curr_cols": "**Colunas do Currículo:** ",
        "map_curr_title": "### Mapear Colunas do Currículo",
        "lbl_col_for": "Coluna para",
        "map_success": "Mapeamento curricular foi implementado com sucesso.",
        "map_err": "Erro ao aplicar o mapeamento:",
        "curr_config_alert": "A configuração do currículo guiará as recomendações do Gemma.",
        "btn_back_upload": "✅ Voltar ao Upload do Professor",
        "upload_title": "## Carregar Dados de Desempenho dos Alunos",
        "upload_desc": "Carregue um arquivo Excel ou CSV com as notas, frequência, matérias, tópicos e competências dos alunos.",
        "btn_download_template": "Baixar Modelo de Excel",
        "lbl_browse_student": "Buscar arquivo Excel ou CSV de alunos",
        "lbl_teacher_inst": "Instruções adicionais do professor para o Gemma",
        "val_teacher_inst": "Concentre-se em alunos com baixa frequência e notas baixas. Recomende atividades simples que não exijam internet ou materiais caros.",
        "student_uploaded_success": "Arquivo de dados dos alunos carregado com sucesso.",
        "map_student_title": "### Mapear Colunas do Arquivo de Alunos",
        "btn_apply_student_map": "Aplicar Mapeamento de Alunos",
        "missing_cols_err": "Faltam colunas obrigatórias após o mapeamento: ",
        "student_map_success": "Mapeamento aplicado e dados carregados com sucesso.",
        "student_map_err": "Erro ao aplicar o mapeamento de alunos:",
        "no_file_info": "Nenhum arquivo carregado ainda. O aplicativo usará dados de amostra para a demonstração.",
        "model_time_info": "A geração de recomendações com o modelo selecionado pode levar vários segundos por aluno.",
        "no_curr_warn": "⚠️ Nenhum currículo anexado (admin_curriculum_example.csv).",
        "no_curr_info": "Será realizada uma avaliação sem currículo base, limitando as recomendações às boas práticas gerais.",
        "chk_understand": "Compreendo, continuar sem um currículo personalizado",
        "btn_go_curr": "❌ Ir para configurar currículo",
        "btn_analyze_gaps": "Analisar lacunas com IA",
        "err_missing_pre_analysis": "Faltam colunas obrigatórias antes da análise: ",
        "err_ollama_gen": "Ocorreu um erro durante a geração de recomendações no Ollama. Verifique a disponibilidade do modelo.",
        "err_gen_rec_outer": "Erro ao gerar recomendações: ",
        "insights_badge": "✨ Análise da IA",
        "dash_title": "## Painel de Análise do Professor",
        "metric_students": "Alunos analisados",
        "metric_avg": "Média da turma",
        "metric_at_risk": "Alunos que precisam de apoio",
        "metric_weakest": "Matéria mais fraca",
        "chart_title": "## Áreas de Aprendizagem Fracas por Matéria",
        "rec_per_student_title": "## Recomendações por Aluno",
        "card_ai_rec": "<h3>🤖 Recomendações de IA</h3><div class='recommendation'>Use exemplos visuais e objetos do ambiente para temas fracos.</div><div class='recommendation'>Crie pequenos grupos de apoio para alunos com lacunas semelhantes.</div><div class='recommendation'>Aplique avaliações curtas semanais para medir o progresso.</div>",
        "card_weekly": "<h3>📅 Plano Semanal</h3><div class='recommendation'><b>Segunda-feira:</b> Revisão guiada de temas fracos.</div><div class='recommendation'><b>Quarta-feira:</b> Prática em pequenos grupos.</div><div class='recommendation'><b>Sexta-feira:</b> Mini avaliação e feedback.</div>",
        "card_responsible": "<h3>🧭 IA Responsável</h3><div class='recommendation'>As recomendações estão alinhadas com as diretrizes curriculares.</div><div class='recommendation'>O sistema evita rotular os alunos negativamente.</div><div class='recommendation'>O professor mantém o controle das decisões.</div>",
        "btn_back_index": "Voltar ao Início",
        "prompt_lang": "Portuguese",
        "none_select": "-- Nenhuma --",
        "lbl_applied": "Aplicado com sucesso",
        "nav_heading": "🧭 Navegação",
        "nav_diagnostics": "📊 Diagnóstico de Desempenho",
        "nav_chat": "💬 Tutor Pedagógico Interativo",
        "chat_welcome": "Olá! Sou o seu tutor pedagógico local. Como posso ajudar você a planejar estratégias didáticas ou exercícios sob medida hoje?",
        "chat_placeholder": "Pergunte ao seu assistente educacional local...",
        "chat_badge": "💬 Chat de Mentoria de IA",
        "lbl_no_models_warn": "⚠️ Nenhum modelo Gemma local detectado. Mostrando alvos de entrega.",
        "lbl_gap_out": "Lacuna de Aprendizagem",
        "lbl_act_out": "Atividade de Reforço",
        "lbl_guide_out": "Guia do Professor"
    },
    "Français": {
        "title": "📚 Teacher Coach AI",
        "subtitle": "Assistant pédagogique hors ligne propulsé par Gemma pour les écoles rurales.",
        "badge_offline": "📴 Local · Faible Coût · Prêt pour le Mode Hors Ligne",
        "welcome_title": "## Bienvenue, enseignant",
        "welcome_desc": "Analysez les notes des élèves, identifiez les lacunes d'apprentissage et recevez des recommandations pratiques pour améliorer les performances en classe, même dans les endroits sans Internet.",
        "bullet_points": "- 📊 Analyse des performances des élèves\n- 🤖 Recommandations d'IA avec Gemma\n- 🧭 Alignement sur le programme\n- 👩‍🏫 Suivi personnalisé par élève",
        "login_card_title": "### Connexion Enseignant",
        "lbl_username": "Identifiant",
        "lbl_password": "Mot de passe",
        "btn_login": "Se connecter",
        "btn_logout": "Se déconnecter",
        "err_login": "Identifiant ou mot de passe incorrect. Utilisez admin/admin.",
        "setup_badge": "🤖 Configuration de l'analyse d'IA",
        "tab_teacher": "Téléchargement Enseignant",
        "tab_admin": "Programme Administrateur",
        "admin_title": "## Configuration du programme de base",
        "admin_desc": "Téléchargez le contenu officiel, le programme national ou le plan de cours de base. Cela devient le cadre éducatif minimal que Gemma doit suivre.",
        "lbl_curr_source": "Source du programme",
        "lbl_grade": "Niveau d'études",
        "lbl_subject": "Matière",
        "lbl_browse_curr": "Parcourir le fichier du programme d'études (Excel/CSV/PDF/Docx)",
        "lbl_align_inst": "Instructions d'alignement sur le programme",
        "curr_saved": "Programme enregistré avec succès.",
        "curr_err": "Erreur lors de la lecture du fichier du programme :",
        "file_saved": "Fichier enregistré localement sous :",
        "curr_preview": "### Aperçu du Programme Scolaire",
        "curr_cols": "**Colonnes du Programme :** ",
        "map_curr_title": "### Mapper les Colonnes du Programme",
        "lbl_col_for": "Colonne pour",
        "map_success": "Mappage du programme appliqué avec succès.",
        "map_err": "Erreur lors de l'application du mappage :",
        "curr_config_alert": "La configuration du programme guidera les recommandations de Gemma.",
        "btn_back_upload": "✅ Retour au téléchargement",
        "upload_title": "## Télécharger les Données des Élèves",
        "upload_desc": "Téléchargez un fichier Excel ou CSV contenant les notes, l'assiduité, les matières, les sujets et les compétences des élèves.",
        "btn_download_template": "Télécharger le modèle Excel",
        "lbl_browse_student": "Parcourir le fichier Excel ou CSV des élèves",
        "lbl_teacher_inst": "Instructions supplémentaires pour Gemma",
        "val_teacher_inst": "Concentrez-vous sur les élèves ayant une faible assiduité et des notes basses. Recommandez des activités simples qui ne nécessitent ni connexion Internet ni matériel coûteux.",
        "student_uploaded_success": "Fichier de données des élèves téléchargé avec succès.",
        "map_student_title": "### Mapper les Colonnes du Fichier des Élèves",
        "btn_apply_student_map": "Appliquer le Mappage des Élèves",
        "missing_cols_err": "Colonnes requises manquantes après le mappage : ",
        "student_map_success": "Mappage appliqué et données chargées avec succès.",
        "student_map_err": "Erreur lors de l'application du mappage des élèves :",
        "no_file_info": "Aucun fichier téléchargé pour le moment. L'application utilisera des données d'exemple pour la démonstration.",
        "model_time_info": "La génération de recommandations avec le modèle sélectionné peut prendre plusieurs secondes par élève.",
        "no_curr_warn": "⚠️ Aucun programme associé trouvé (admin_curriculum_example.csv).",
        "no_curr_info": "Une évaluation sans programme de base sera effectuée, limitant les recommandations aux bonnes pratiques générales.",
        "chk_understand": "Je comprends, continuer sans programme personnalisé",
        "btn_go_curr": "❌ Aller à la configuration du programme",
        "btn_analyze_gaps": "Analyser les lacunes avec l'IA",
        "err_missing_pre_analysis": "Colonnes requises manquantes avant l'analyse : ",
        "err_ollama_gen": "Une erreur est survenue lors de la génération avec Ollama. Veuillez vérifier la disponibilité du modèle.",
        "err_gen_rec_outer": "Erreur lors de la génération des recommandations : ",
        "insights_badge": "✨ Analyse de l'IA",
        "dash_title": "## Tableau de Bord de l'Enseignant",
        "metric_students": "Élèves analysés",
        "metric_avg": "Moyenne de la classe",
        "metric_at_risk": "Élèves ayant besoin de soutien",
        "metric_weakest": "Matière la plus faible",
        "chart_title": "## Domaines d'Apprentissage Faibles par Matière",
        "rec_per_student_title": "## Recommandations par Élève",
        "card_ai_rec": "<h3>🤖 Recommandations d'IA</h3><div class='recommendation'>Utilisez des exemples visuels et des objets de l'environnement pour les sujets faibles.</div><div class='recommendation'>Créez de petits groupes de soutien pour les élèves ayant des lacunes similaires.</div><div class='recommendation'>Appliquez de courtes évaluations hebdomadaires pour les progrès.</div>",
        "card_weekly": "<h3>📅 Plan Hebdomadaire</h3><div class='recommendation'><b>Lundi :</b> Révision guidée des sujets faibles.</div><div class='recommendation'><b>Mercredi :</b> Pratique en petits groupes.</div><div class='recommendation'><b>Vendredi :</b> Mini-évaluation et feedback.</div>",
        "card_responsible": "<h3>🧭 IA Responsable</h3><div class='recommendation'>Les recommandations sont alignées sur le programme scolaire.</div><div class='recommendation'>Le système évite de stigmatiser négativement les élèves.</div><div class='recommendation'>L'enseignant reste maître des décisions.</div>",
        "btn_back_index": "Retour à l'Accueil",
        "prompt_lang": "French",
        "none_select": "-- Aucun --",
        "lbl_applied": "Appliqué avec succès",
        "nav_heading": "🧭 Navigation",
        "nav_diagnostics": "📊 Diagnostic des Performances",
        "nav_chat": "💬 Conseiller Pédagogique Interactif",
        "chat_welcome": "Bonjour ! Je suis votre conseiller pédagogique local. Comment puis-je vous aider à concevoir des stratégies ou des exercices aujourd'hui ?",
        "chat_placeholder": "Demandez à votre assistant pédagogique local...",
        "chat_badge": "💬 Chat de mentorat IA",
        "lbl_no_models_warn": "⚠️ Aucun modèle Gemma local détecté. Affichage des cibles.",
        "lbl_gap_out": "Écart d'Apprentissage",
        "lbl_act_out": "Activité de Renforcement",
        "lbl_guide_out": "Guide de l'Enseignant"
    }
}

# ==========================================
# Core Functions Definition Block (Python Roadmap)
# ==========================================
def get_local_gemma_models():
    """Interrogates local Ollama daemon to find downloaded variants safely."""
    try:
        response = ollama.list()
        models_list = []
        if hasattr(response, 'models'):
            models_list = response.models
        elif isinstance(response, dict):
            models_list = response.get('models', [])
        else:
            models_list = getattr(response, 'models', [])

        gemma_detected = []
        for model in models_list:
            name = ""
            if hasattr(model, 'model'): name = model.model
            elif hasattr(model, 'name'): name = model.name
            elif isinstance(model, dict): name = model.get('name', model.get('model', ''))
            
            if name and 'gemma' in name.lower():
                gemma_detected.append(name)
        return gemma_detected
    except Exception:
        return []

# Robust Master Mock Data Definition
sample_data = pd.DataFrame({
    "Student": ["Ana", "Luis", "Marta", "Carlos", "Sofia", "Pedro", "Elena", "Diego"],
    "Grade": [5, 5, 5, 5, 5, 5, 5, 5],
    "Subject": ["Math", "Reading", "Math", "Science", "Math", "Reading", "Math", "Science"],
    "Topic": ["Fractions", "Main Idea", "Decimals", "Plants", "Fractions", "Inference", "Fractions", "Water Cycle"],
    "Competency": ["Problem Solving", "Comprehension", "Numerical Reasoning", "Observation", "Problem Solving", "Inference", "Problem Solving", "Scientific Thinking"],
    "Score": [58, 62, 55, 72, 61, 69, 57, 75],
    "Attendance": [82, 90, 78, 95, 88, 80, 76, 92],
    "Objective": ["Improve classroom performance"] * 8,
    "Resources": ["Notebook, board, local objects"] * 8,
    "Teaching_Method": ["Guided practice"] * 8,
    "Evaluation_Type": ["Short quiz"] * 8
})

required_columns = ["Student", "Grade", "Subject", "Topic", "Competency", "Score", "Attendance"]

def create_template():
    output = BytesIO()
    sample_data.to_excel(output, index=False, engine="openpyxl")
    output.seek(0)
    return output

def load_uploaded_dataframe(uploaded_file):
    content = uploaded_file.getvalue()
    if uploaded_file.name.lower().endswith(".csv"):
        return pd.read_csv(BytesIO(content))
    return pd.read_excel(BytesIO(content))

def save_uploaded_file(uploaded_file, save_dir):
    save_dir.mkdir(parents=True, exist_ok=True)
    file_path = save_dir / Path(uploaded_file.name).name
    with open(file_path, "wb") as out_file:
        out_file.write(uploaded_file.getvalue())
    return file_path

def validate_file(df):
    return [col for col in required_columns if col not in df.columns]

def build_curriculum_description():
    curriculum_df = st.session_state.get("curriculum_df")
    if curriculum_df is None or curriculum_df.empty:
        return ""

    text = "Curriculum guidelines found:\n"
    target_columns = ["Subject", "Topic", "Objectives", "Contents", "Indicators", "Activities"]
    available_cols = [c for c in target_columns if c in curriculum_df.columns]
    
    if not available_cols:
        available_cols = list(curriculum_df.columns[:4])

    for index, row in curriculum_df.head(5).fillna("").iterrows():
        parts = [f"{col}: {row[col]}" for col in available_cols if str(row[col]).strip()]
        if parts:
            text += f"{index + 1}. " + "; ".join(parts) + "\n"
    return text

def get_gemma_recommendation(row, model_name, curriculum_description, target_lang, labels_out):
    gap_lbl, act_lbl, guide_lbl = labels_out
    prompt = f"""
Respond STRICTLY and ONLY in {target_lang}.
Do not greet. Do not say "Hello". Do not say "As Gemma". Do not explain that you are an AI.

Respond using exactly this layout structure format structure:
{gap_lbl}:

{act_lbl}:

{guide_lbl}:

Maximum 80 words.

Student Performance Context Parameters:
- Name: {row.get('Student', '')}
- Grade: {row.get('Grade', '')}
- Subject: {row.get('Subject', '')}
- Topic: {row.get('Topic', '')}
- Competency: {row.get('Competency', '')}
- Score: {row.get('Score', '')}
- Attendance: {row.get('Attendance', '')}
"""

    if curriculum_description:
        prompt += f"\nTake into account the following school curriculum framework:\n{curriculum_description}\nSuggest reinforcement activities aligned with indicators."
    else:
        prompt += """
No institutional curriculum framework was found.
Generate open pedagogical recommendations using educational best practices for low-resource classrooms.
CRITICAL DESIGN RULE: Do not assume internet access or expensive materials. Propose exercises using standard notebooks, blackboards, or environmental objects.
"""

    prompt += f"\nRemember: Generate the entire response layout block strictly in {target_lang}."

    try:
        response = ollama.chat(
            model=model_name,
            messages=[
                {"role": "system", "content": f"You are a helpful local educational advisor. You respond briefly, directly, and exclusively in {target_lang}."},
                {"role": "user", "content": prompt}
            ],
            options={
                "num_ctx": 8192,       # 🎯 Espacio suficiente para el RAG de MEDUCA
                "num_predict": 1200,   # 🚀 El cambio clave: Le da presupuesto a Gemma para pensar Y escribir la respuesta
                "temperature": 0.3,    # 🔥 Mantiene el formato estructurado y evita divagaciones
            }
        )
        
        # Cross-version parser block to guarantee response extraction
        if hasattr(response, 'message') and hasattr(response.message, 'content'):
            return response.message.content.strip()
        elif isinstance(response, dict):
            return response.get("message", {}).get("content", "").strip()
        else:
            return response["message"]["content"].strip()
            
    except Exception as e:
        return f"Error generating recommendation: {e}"

def generate_gemma_recommendations(df, model_name, curriculum_description, target_lang, labels_out):
    records = df.to_dict(orient="records")
    total = len(records)
    progress = st.progress(0)
    status_text = st.empty()
    recommendations = [None] * total
    completed = 0

    # 🚀 CONTROLLED SINGLE WORKER THREAD PIPELINE TO AVOID CPU CONTEXT OVERHEAD
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future_to_index = {
            executor.submit(get_gemma_recommendation, row, model_name, curriculum_description, target_lang, labels_out): i 
            for i, row in enumerate(records)
        }
        for future in concurrent.futures.as_completed(future_to_index):
            i = future_to_index[future]
            try:
                recommendations[i] = future.result()
            except Exception as e:
                recommendations[i] = f"Error: {e}"
            completed += 1
            progress.progress(int(completed / total * 100))
            status_text.text(f"⚡ Processing: {completed} of {total} students completed using {model_name}...")
            
    progress.empty()
    status_text.empty()
    return recommendations

def analyze_students(df, model_name, curriculum_description, target_lang, labels_out):
    df = df.copy()
    df["Score"] = pd.to_numeric(df["Score"], errors="coerce")
    df["Attendance"] = pd.to_numeric(df["Attendance"], errors="coerce")

    def risk(row):
        if row["Score"] < 60 or row["Attendance"] < 80: return "High"
        if row["Score"] < 70: return "Medium"
        return "Low"

    df["Risk_Level"] = df.apply(risk, axis=1)
    df["Gemma_4_Recommendation"] = generate_gemma_recommendations(df, model_name, curriculum_description, target_lang, labels_out)

    summary = {
        "students": df["Student"].nunique(),
        "average": round(df["Score"].mean(), 1),
        "at_risk": df[df["Risk_Level"].isin(["High", "Medium"])]["Student"].nunique(),
        "weakest_subject": df.groupby("Subject")["Score"].mean().sort_values().index[0],
    }
    return df, summary

# ==========================================
# Application State Initialization Controller
# ==========================================
if "screen" not in st.session_state:
    st.session_state.screen = "login"
if "ui_lang" not in st.session_state:
    st.session_state.ui_lang = "English"
if "current_page" not in st.session_state:
    st.session_state.current_page = "Diagnostics"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "df" not in st.session_state:
    st.session_state.df = sample_data.copy()
if "analysis" not in st.session_state:
    st.session_state.analysis = None
if "force_curriculum_view" not in st.session_state:
    st.session_state.force_curriculum_view = False
if "curriculum_df" not in st.session_state:
    try:
        st.session_state.curriculum_df = pd.read_csv("data/admin_curriculum_example.csv")
    except Exception:
        st.session_state.curriculum_df = None

# ==========================================
# Sidebar Execution View (Safe Order Placement)
# ==========================================
st.sidebar.markdown("### 🌍 Language / Idioma")
selected_lang = st.sidebar.selectbox(
    "Interface Language", 
    ["English", "Español", "Português", "Français"], 
    index=["English", "Español", "Português", "Français"].index(st.session_state.ui_lang)
)
st.sidebar.markdown("---")
st.session_state.ui_lang = selected_lang
t = I18N[st.session_state.ui_lang]

# Execute Dynamic Local Discovering Service
discovered_models = get_local_gemma_models()

if discovered_models:
    OLLAMA_MODELS = discovered_models
else:
    OLLAMA_MODELS = ["gemma4:e2b", "gemma4:e4b", "gemma4:26b", "gemma4:31b"]
    st.sidebar.warning(t["lbl_no_models_warn"])

selected_model = st.sidebar.selectbox("Select Gemma/Ollama model", OLLAMA_MODELS, index=0)
st.session_state.selected_model = selected_model

# Page Navigation Router
if st.session_state.screen != "login":
    st.sidebar.markdown(f"### {t['nav_heading']}")
    nav_options = {t['nav_diagnostics']: "Diagnostics", t['nav_chat']: "Chat"}
    current_index = list(nav_options.values()).index(st.session_state.current_page)
    selected_nav = st.sidebar.radio("Menu", list(nav_options.keys()), index=current_index, label_visibility="collapsed")
    st.session_state.current_page = nav_options[selected_nav]

# Render Core CSS Style Elements Layout
st.markdown("""
<style>
.block-container { padding-top: 2rem; padding-bottom: 3rem; }
.title { font-size:42px; font-weight:900; color:#0f172a; margin-bottom:6px; }
.subtitle { font-size:18px; color:#475569; margin-bottom:24px; }
.card { background:white; padding:24px; border-radius:24px; border:1px solid #e2e8f0; box-shadow:0 12px 35px rgba(15,23,42,.08); margin-bottom:18px; }
.badge { display:inline-block; background:#eef6ff; color:#1d4ed8; padding:8px 14px; border-radius:999px; font-weight:800; margin-bottom:12px; }
.offline { background:#fef3c7; color:#92400e; }
.metric { background:white; padding:20px; border-radius:20px; border:1px solid #e2e8f0; box-shadow:0 10px 25px rgba(15,23,42,.06); }
.metric-label { color:#64748b; font-size:14px; font-weight:700; }
.metric-value { color:#0f172a; font-size:32px; font-weight:900; }
.recommendation { background:#f8fafc; border:1px solid #e2e8f0; padding:14px; border-radius:16px; margin-bottom:10px; color:#334155; }
</style>
""", unsafe_allow_html=True)

st.markdown(f"<div class='title'>{t['title']}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='subtitle'>{t['subtitle']}</div>", unsafe_allow_html=True)

# ==========================================
# Routing Pages Engine Controller Logic
# ==========================================
if st.session_state.screen == "login":
    col1, col2 = st.columns([1.2, 0.8])
    with col1:
        st.markdown(f"<span class='badge offline'>{t['badge_offline']}</span>", unsafe_allow_html=True)
        st.markdown(t['welcome_title'])
        st.write(t['welcome_desc'])
        st.markdown(t['bullet_points'])
    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown(t['login_card_title'])
        username = st.text_input(t['lbl_username'], value=st.session_state.get("username", ""))
        password = st.text_input(t['lbl_password'], type="password", value=st.session_state.get("password", "admin"))
        if st.button(t['btn_login'], width='stretch'):
            if username == "admin" and password == "admin":
                st.session_state.username = username
                st.session_state.password = password
                st.session_state.screen = "index"
                st.session_state.logged_in = True
                st.rerun()
            else: st.error(t['err_login'])
        st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.screen == "index" and st.session_state.current_page == "Diagnostics":
    st.markdown(f"<span class='badge'>{t['setup_badge']}</span>", unsafe_allow_html=True)
    
    if st.session_state.get("force_curriculum_view", False):
        st.markdown(t['admin_title'])
        st.write(t['admin_desc'])
        curriculum_source = st.selectbox(t['lbl_curr_source'], ["MEDUCA", "National Ministry", "Director Guidelines"])
        uploaded_curriculum = st.file_uploader(t['lbl_browse_curr'], type=["xlsx", "csv"])
        
        if uploaded_curriculum:
            try:
                st.session_state.curriculum_df = load_uploaded_dataframe(uploaded_curriculum)
                st.success(t['curr_saved'])
            except Exception as e: st.error(f"{t['curr_err']} {e}")

        if st.session_state.get("curriculum_df") is not None:
            st.markdown(t['curr_preview'])
            st.dataframe(st.session_state.curriculum_df.head(10), width='stretch')
            
        if st.button(t['btn_back_upload'], width='stretch'):
            st.session_state.force_curriculum_view = False
            st.rerun()
    else:
        tab1, tab2 = st.tabs([t['tab_teacher'], t['tab_admin']])
        with tab2:
            st.markdown(t['admin_title'])
            st.write(t['admin_desc'])
            uploaded_curriculum = st.file_uploader(t['lbl_browse_curr'], type=["xlsx", "csv"], key="tab2_upload")
            if uploaded_curriculum:
                try:
                    st.session_state.curriculum_df = load_uploaded_dataframe(uploaded_curriculum)
                    st.success(t['lbl_applied'])
                except Exception as e: st.error(str(e))

            if st.session_state.get("curriculum_df") is not None:
                st.markdown(t['curr_preview'])
                st.dataframe(st.session_state.curriculum_df.head(5), width='stretch')

        with tab1:
            st.markdown(t['upload_title'])
            st.write(t['upload_desc'])
            st.download_button(t['btn_download_template'], data=create_template(), file_name="template.xlsx")
            uploaded_file = st.file_uploader(t['lbl_browse_student'], type=["xlsx", "csv"])
            st.text_area(t['lbl_teacher_inst'], value=t['val_teacher_inst'])

            if uploaded_file:
                try:
                    st.session_state.df = load_uploaded_dataframe(uploaded_file)
                    st.success(t['student_uploaded_success'])
                    st.dataframe(st.session_state.df.head(5), width='stretch')
                except Exception as e: st.error(str(e))
            else: st.info(t['no_file_info'])

            st.info(t['model_time_info'])
            
            curriculum_exists = st.session_state.get("curriculum_df") is not None
            can_proceed = True

            if not curriculum_exists:
                st.warning(t['no_curr_warn'])
                st.info(t['no_curr_info'])
                can_proceed = st.checkbox(t['chk_understand'], key="confirm_skip_curr")
                if not can_proceed and st.button(t['btn_go_curr'], width='stretch'):
                     st.session_state.force_curriculum_view = True
                     st.rerun()

            if can_proceed:
                if st.button(t['btn_analyze_gaps'], width='stretch'):
                    missing = validate_file(st.session_state.df)
                    if missing: st.error(t['err_missing_pre_analysis'] + ", ".join(missing))
                    else:
                        try:
                            curr_desc = build_curriculum_description()
                            labels_out = (t['lbl_gap_out'], t['lbl_act_out'], t['lbl_guide_out'])
                            final_df, summary = analyze_students(st.session_state.df, st.session_state.selected_model, curr_desc, t['prompt_lang'], labels_out)
                            st.session_state.analysis = {"df": final_df, "summary": summary}
                            st.session_state.screen = "dashboard"
                            st.rerun()
                        except Exception as e: st.error(t['err_gen_rec_outer'] + str(e))

        if st.button(t['btn_logout'], key="logout_index"):
            st.session_state.screen = "login"
            st.rerun()

elif st.session_state.screen == "dashboard" and st.session_state.current_page == "Diagnostics":
    df = st.session_state.analysis["df"]
    summary = st.session_state.analysis["summary"]
    st.markdown(f"<span class='badge'>{t['insights_badge']}</span>", unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f"<div class='metric'><div class='metric-label'>{t['metric_students']}</div><div class='metric-value'>{summary['students']}</div></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='metric'><div class='metric-label'>{t['metric_avg']}</div><div class='metric-value'>{summary['average']}%</div></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='metric'><div class='metric-label'>{t['metric_at_risk']}</div><div class='metric-value'>{summary['at_risk']}</div></div>", unsafe_allow_html=True)
    c4.markdown(f"<div class='metric'><div class='metric-label'>{t['metric_weakest']}</div><div class='metric-value' style='font-size:22px'>{summary['weakest_subject']}</div></div>", unsafe_allow_html=True)

    st.markdown(t['chart_title'])
    st.bar_chart(df.groupby("Subject")["Score"].mean())

    st.markdown(t['rec_per_student_title'])
    st.dataframe(df[["Student", "Grade", "Subject", "Topic", "Score", "Attendance", "Risk_Level", "Gemma_4_Recommendation"]], width='stretch')

    col1, col2, col3 = st.columns(3)
    col1.markdown(f"<div class='card'>{t['card_ai_rec']}</div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='card'>{t['card_weekly']}</div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='card'>{t['card_responsible']}</div>", unsafe_allow_html=True)

    if st.button(t['btn_back_index']):
        st.session_state.screen = "index"
        st.rerun()

elif st.session_state.current_page == "Chat":
    st.markdown(f"<span class='badge'>{t['chat_badge']}</span>", unsafe_allow_html=True)
    st.markdown(f"## {t['nav_chat']}")
    st.info(f"⚡ Connected to local model: **{st.session_state.selected_model}** (100% Offline Mode)")

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if not st.session_state.chat_history:
        with st.chat_message("assistant"): st.markdown(t['chat_welcome'])

    if user_query := st.chat_input(t['chat_placeholder']):
        with st.chat_message("user"): st.markdown(user_query)
        st.session_state.chat_history.append({"role": "user", "content": user_query})

        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            try:
                system_prompt = f"You are a professional educational consultant mentor. Help the teacher design local strategies. Respond strictly and only in {t['prompt_lang']}."
                response = ollama.chat(
                    model=st.session_state.selected_model,
                    messages=[{"role": "system", "content": system_prompt}, *st.session_state.chat_history],
                    options={
                        "num_ctx": 8192,       # 🎯 Espacio suficiente para el RAG de MEDUCA
                        "num_predict": 1200,   # 🚀 El cambio clave: Le da presupuesto a Gemma para pensar Y escribir la respuesta
                        "temperature": 0.3,    # 🔥 Mantiene el formato estructurado y evita divagaciones
                    }
                )
                
                # Cross-version content discovery parser mapping loop
                if hasattr(response, 'message') and hasattr(response.message, 'content'):
                    assistant_response = response.message.content.strip()
                elif isinstance(response, dict):
                    assistant_response = response.get("message", {}).get("content", "").strip()
                else:
                    assistant_response = response["message"]["content"].strip()

                response_placeholder.markdown(assistant_response)
                st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})
            except Exception as e: response_placeholder.error(f"Error calling local model: {e}")
        st.rerun()
