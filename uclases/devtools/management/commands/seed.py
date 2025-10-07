"""
Management command para poblar la base de datos con datos de prueba
Ejecutar con: python manage.py seed
O en producción: python manage.py seed --force
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction
from django.contrib.auth import get_user_model
from django.db.models import Count
import random
from datetime import time

from courses.models import Ramo, Carrera, OfertaClase, SolicitudClase, PerfilRamo, HorarioOfertado
from courses.enums import DiaSemana
from accounts.models import Perfil

User = get_user_model()


class Command(BaseCommand):
    help = "Poblar la base de datos con datos de prueba (idempotente - puede ejecutarse múltiples veces)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Permitir ejecución fuera de modo DEBUG"
        )

    @transaction.atomic
    def handle(self, *args, **opts):
        # Verificar si estamos en DEBUG o si se pasó --force
        if not settings.DEBUG and not opts["force"]:
            self.stderr.write(
                self.style.ERROR(
                    "❌ Negado: Este comando solo se ejecuta en DEBUG=True. "
                    "Use --force para ejecutar en producción."
                )
            )
            return

        self.stdout.write(self.style.SUCCESS("🚀 Iniciando población de base de datos..."))

        # ============================================
        # 1. CREAR CARRERAS
        # ============================================
        self.stdout.write("\n📚 Creando carreras...")
        carreras_data = [
            "Ingeniería Civil en Computación",
            "Ingeniería Civil Industrial",
            "Ingeniería Civil Eléctrica",
            "Ingeniería Civil Mecánica",
            "Ingeniería Civil Matemática",
            "Licenciatura en Ciencias de la Computación",
            "Ingeniería Civil",
            "Ingeniería Comercial",
        ]

        carreras = []
        for nombre in carreras_data:
            carrera, created = Carrera.objects.get_or_create(name=nombre)
            carreras.append(carrera)
            if created:
                self.stdout.write(f"  ✅ Creada: {nombre}")
            else:
                self.stdout.write(self.style.WARNING(f"  ⚠️  Ya existe: {nombre}"))

        # ============================================
        # 2. CREAR RAMOS
        # ============================================
        self.stdout.write("\n📖 Creando ramos...")
        ramos_data = [
            # Matemáticas
            "Álgebra Lineal",
            "Cálculo I",
            "Cálculo II",
            "Cálculo III",
            "Ecuaciones Diferenciales",
            "Álgebra Abstracta",
            "Probabilidades y Estadística",
            "Análisis Numérico",
            # Física
            "Física I",
            "Física II",
            "Física III",
            "Física Experimental",
            # Computación
            "Programación",
            "Estructuras de Datos",
            "Algoritmos",
            "Bases de Datos",
            "Ingeniería de Software",
            "Sistemas Operativos",
            "Redes de Computadores",
            "Inteligencia Artificial",
            "Machine Learning",
            "Desarrollo Web",
            # Otros
            "Química General",
            "Economía",
            "Gestión de Proyectos",
            "Inglés Técnico",
        ]

        ramos = []
        for nombre in ramos_data:
            ramo, created = Ramo.objects.get_or_create(name=nombre)
            ramos.append(ramo)
            if created:
                self.stdout.write(f"  ✅ Creado: {nombre}")

        # ============================================
        # 3. CREAR USUARIOS PROFESORES
        # ============================================
        self.stdout.write("\n👨‍🏫 Creando profesores...")
        profesores_data = [
            {"username": "profMatematicas", "email": "mat@uclases.cl", "first_name": "Carlos", "last_name": "Martínez", "carrera": carreras[4]},
            {"username": "profFisica", "email": "fis@uclases.cl", "first_name": "Laura", "last_name": "González", "carrera": carreras[2]},
            {"username": "profProgramacion", "email": "prog@uclases.cl", "first_name": "Diego", "last_name": "Rodríguez", "carrera": carreras[0]},
            {"username": "profAlgoritmos", "email": "algo@uclases.cl", "first_name": "María", "last_name": "Silva", "carrera": carreras[5]},
            {"username": "profBaseDatos", "email": "bd@uclases.cl", "first_name": "Roberto", "last_name": "Fernández", "carrera": carreras[0]},
            {"username": "profIA", "email": "ia@uclases.cl", "first_name": "Andrea", "last_name": "López", "carrera": carreras[0]},
            {"username": "profWeb", "email": "web@uclases.cl", "first_name": "Felipe", "last_name": "Torres", "carrera": carreras[0]},
        ]

        profesores = []
        for data in profesores_data:
            if User.objects.filter(username=data["username"]).exists():
                user = User.objects.get(username=data["username"])
                self.stdout.write(self.style.WARNING(f"  ⚠️  Ya existe: {data['username']}"))
            else:
                user = User.objects.create_user(
                    username=data["username"],
                    email=data["email"],
                    password="password123",
                    first_name=data["first_name"],
                    last_name=data["last_name"]
                )
                self.stdout.write(f"  ✅ Creado: {data['username']} ({data['first_name']} {data['last_name']})")
            
            # Actualizar perfil
            perfil = user.perfil
            perfil.carrera = data["carrera"]
            perfil.descripcion = f"Profesor con experiencia en {data['carrera'].name}. Disponible para clases particulares."
            perfil.telefono = f"+5691234567{len(profesores)}"
            perfil.save()
            profesores.append(perfil)

        # ============================================
        # 4. CREAR USUARIOS ESTUDIANTES
        # ============================================
        self.stdout.write("\n👨‍🎓 Creando estudiantes...")
        estudiantes_data = [
            {"username": "juan_perez", "email": "juan@uclases.cl", "first_name": "Juan", "last_name": "Pérez", "carrera": carreras[0]},
            {"username": "ana_garcia", "email": "ana@uclases.cl", "first_name": "Ana", "last_name": "García", "carrera": carreras[1]},
            {"username": "pedro_sanchez", "email": "pedro@uclases.cl", "first_name": "Pedro", "last_name": "Sánchez", "carrera": carreras[0]},
            {"username": "sofia_rojas", "email": "sofia@uclases.cl", "first_name": "Sofía", "last_name": "Rojas", "carrera": carreras[5]},
            {"username": "diego_munoz", "email": "diego@uclases.cl", "first_name": "Diego", "last_name": "Muñoz", "carrera": carreras[2]},
            {"username": "valentina_castro", "email": "vale@uclases.cl", "first_name": "Valentina", "last_name": "Castro", "carrera": carreras[0]},
            {"username": "matias_vera", "email": "matias@uclases.cl", "first_name": "Matías", "last_name": "Vera", "carrera": carreras[3]},
            {"username": "camila_flores", "email": "camila@uclases.cl", "first_name": "Camila", "last_name": "Flores", "carrera": carreras[1]},
            {"username": "nicolas_herrera", "email": "nico@uclases.cl", "first_name": "Nicolás", "last_name": "Herrera", "carrera": carreras[4]},
            {"username": "isidora_pino", "email": "isi@uclases.cl", "first_name": "Isidora", "last_name": "Pino", "carrera": carreras[0]},
        ]

        estudiantes = []
        for data in estudiantes_data:
            if User.objects.filter(username=data["username"]).exists():
                user = User.objects.get(username=data["username"])
                self.stdout.write(self.style.WARNING(f"  ⚠️  Ya existe: {data['username']}"))
            else:
                user = User.objects.create_user(
                    username=data["username"],
                    email=data["email"],
                    password="password123",
                    first_name=data["first_name"],
                    last_name=data["last_name"]
                )
                self.stdout.write(f"  ✅ Creado: {data['username']} ({data['first_name']} {data['last_name']})")
            
            # Actualizar perfil
            perfil = user.perfil
            perfil.carrera = data["carrera"]
            perfil.descripcion = f"Estudiante de {data['carrera'].name}. Buscando mejorar mis conocimientos."
            perfil.telefono = f"+5698765432{len(estudiantes)}"
            perfil.save()
            estudiantes.append(perfil)

        # ============================================
        # 5. ASIGNAR RAMOS CURSADOS A PROFESORES
        # ============================================
        self.stdout.write("\n📝 Asignando ramos cursados a profesores...")
        ramos_por_profesor = {
            0: [0, 1, 2, 3, 4, 6],  # profMatematicas
            1: [8, 9, 10, 11],      # profFisica
            2: [12, 13, 14],        # profProgramacion
            3: [13, 14, 15, 17],    # profAlgoritmos
            4: [15, 16],            # profBaseDatos
            5: [19, 20],            # profIA
            6: [21, 16],            # profWeb
        }

        for prof_idx, ramos_indices in ramos_por_profesor.items():
            if prof_idx < len(profesores):
                for ramo_idx in ramos_indices:
                    if ramo_idx < len(ramos):
                        PerfilRamo.objects.get_or_create(
                            perfil=profesores[prof_idx],
                            ramo=ramos[ramo_idx]
                        )
                self.stdout.write(f"  ✅ Asignados {len(ramos_indices)} ramos a {profesores[prof_idx].user.username}")

        # ============================================
        # 6. ASIGNAR RAMOS CURSADOS A ESTUDIANTES
        # ============================================
        self.stdout.write("\n📝 Asignando ramos cursados a estudiantes...")
        for estudiante in estudiantes:
            num_ramos = random.randint(3, 8)
            ramos_estudiante = random.sample(ramos[:15], num_ramos)
            
            for ramo in ramos_estudiante:
                PerfilRamo.objects.get_or_create(
                    perfil=estudiante,
                    ramo=ramo
                )
            self.stdout.write(f"  ✅ Asignados {num_ramos} ramos a {estudiante.user.username}")

        # ============================================
        # 7. CREAR OFERTAS DE CLASES
        # ============================================
        self.stdout.write("\n💼 Creando ofertas de clases...")
        
        # Primero, limpiar duplicados existentes
        # Encontrar ofertas duplicadas y mantener solo la más reciente
        duplicates = OfertaClase.objects.values('profesor', 'titulo').annotate(
            count=Count('id')
        ).filter(count__gt=1)
        
        for dup in duplicates:
            ofertas_dup = OfertaClase.objects.filter(
                profesor=dup['profesor'],
                titulo=dup['titulo']
            ).order_by('-fecha_publicacion')
            # Mantener la primera (más reciente), eliminar el resto
            to_delete = ofertas_dup[1:]
            for oferta in to_delete:
                oferta.delete()
            self.stdout.write(self.style.WARNING(f"  🧹 Limpiadas ofertas duplicadas: {dup['titulo'][:40]}..."))
        
        ofertas_data = [
            {
                "profesor": profesores[0],
                "titulo": "Clases de Cálculo I - Preparación para certámenes",
                "descripcion": "Ofrezco clases de Cálculo I con enfoque en preparación para certámenes. Incluye resolución de ejercicios tipo prueba, revisión de materia y tips para optimizar el tiempo en evaluaciones. 3 años de experiencia ayudando estudiantes.",
                "ramos": [ramos[1]],
            },
            {
                "profesor": profesores[0],
                "titulo": "Álgebra Lineal - Desde cero hasta avanzado",
                "descripcion": "¿Problemas con matrices, vectores o espacios vectoriales? Te ayudo con una metodología clara y ejemplos prácticos. Incluyo material complementario y ejercicios resueltos.",
                "ramos": [ramos[0]],
            },
            {
                "profesor": profesores[1],
                "titulo": "Física I y II - Mecánica y Electricidad",
                "descripcion": "Clases particulares de Física para ingeniería. Énfasis en comprensión conceptual y resolución de problemas. Disponibilidad fines de semana.",
                "ramos": [ramos[8], ramos[9]],
            },
            {
                "profesor": profesores[2],
                "titulo": "Programación en Python - Nivel básico a intermedio",
                "descripcion": "Aprende Python desde cero: variables, estructuras de control, funciones, POO, y más. Incluye proyectos prácticos y código comentado. Ideal para CC1002 o CC3001.",
                "ramos": [ramos[12]],
            },
            {
                "profesor": profesores[2],
                "titulo": "Estructuras de Datos - Listas, árboles, grafos",
                "descripcion": "Domina las estructuras de datos fundamentales. Implementación en Python/Java, análisis de complejidad y aplicaciones prácticas. Material de apoyo incluido.",
                "ramos": [ramos[13]],
            },
            {
                "profesor": profesores[3],
                "titulo": "Algoritmos - Preparación intensiva",
                "descripcion": "Curso completo de algoritmos: ordenamiento, búsqueda, recursión, programación dinámica, greedy. Incluye ejercicios de competencias de programación.",
                "ramos": [ramos[14]],
            },
            {
                "profesor": profesores[4],
                "titulo": "Bases de Datos - SQL y diseño",
                "descripcion": "Aprende SQL desde consultas básicas hasta queries complejas. También cubrimos normalización, diseño ER, y optimización de consultas. PostgreSQL y MySQL.",
                "ramos": [ramos[15]],
            },
            {
                "profesor": profesores[5],
                "titulo": "Introducción a Machine Learning con Python",
                "descripcion": "Aprende los fundamentos de ML: regresión, clasificación, clustering. Usamos scikit-learn, pandas y numpy. Proyectos con datasets reales.",
                "ramos": [ramos[20]],
            },
            {
                "profesor": profesores[6],
                "titulo": "Desarrollo Web Full-Stack - Django + React",
                "descripcion": "Crea aplicaciones web completas desde cero. Backend con Django REST Framework, frontend con React. Incluye despliegue en producción.",
                "ramos": [ramos[21]],
            },
            {
                "profesor": profesores[0],
                "titulo": "Matemáticas para Ingeniería - Paquete completo",
                "descripcion": "Clases de Cálculo I, II, III y Ecuaciones Diferenciales. Ideal para estudiantes que necesitan reforzar toda la línea de cálculo. Descuento por paquete.",
                "ramos": [ramos[1], ramos[2], ramos[3], ramos[4]],
            },
        ]

        ofertas_creadas = []
        for data in ofertas_data:
            oferta, created = OfertaClase.objects.update_or_create(
                profesor=data["profesor"],
                titulo=data["titulo"],
                defaults={"descripcion": data["descripcion"]}
            )
            oferta.ramos.set(data["ramos"])
            ofertas_creadas.append(oferta)
            status = "✅ Creada" if created else "♻️  Actualizada"
            self.stdout.write(f"  {status}: {data['titulo'][:50]}... por {data['profesor'].user.username}")

        # ============================================
        # 7.1. ASIGNAR HORARIOS A LAS OFERTAS
        # ============================================
        self.stdout.write("\n⏰ Asignando horarios a ofertas...")
        
        # Definir rangos de horarios típicos
        horarios_disponibles = [
            (time(8, 0), time(10, 0)),   # 8:00 - 10:00
            (time(10, 0), time(12, 0)),  # 10:00 - 12:00
            (time(12, 0), time(14, 0)),  # 12:00 - 14:00
            (time(14, 0), time(16, 0)),  # 14:00 - 16:00
            (time(16, 0), time(18, 0)),  # 16:00 - 18:00
            (time(18, 0), time(20, 0)),  # 18:00 - 20:00
            (time(20, 0), time(22, 0)),  # 20:00 - 22:00
        ]
        
        for oferta in ofertas_creadas:
            # Eliminar horarios anteriores para hacer idempotente
            oferta.horarios.all().delete()
            
            # Asignar entre 2 y 4 horarios aleatorios
            num_horarios = random.randint(2, 4)
            dias_usados = set()
            
            for _ in range(num_horarios):
                # Elegir un día que no se haya usado aún
                dias_disponibles = [d for d in DiaSemana.values if d not in dias_usados]
                if not dias_disponibles:
                    break
                    
                dia = random.choice(dias_disponibles)
                dias_usados.add(dia)
                
                # Elegir un horario aleatorio
                hora_inicio, hora_fin = random.choice(horarios_disponibles)
                
                # Crear el horario
                HorarioOfertado.objects.create(
                    oferta=oferta,
                    dia=dia,
                    hora_inicio=hora_inicio,
                    hora_fin=hora_fin,
                    cupos_totales=random.randint(1, 5)
                )
            
            dia_nombres = [DiaSemana(d).label for d in sorted(dias_usados)]
            self.stdout.write(f"  ✅ Asignados {len(dias_usados)} horarios a '{oferta.titulo[:40]}...' ({', '.join(dia_nombres)})")

        # ============================================
        # 8. CREAR SOLICITUDES DE CLASES
        # ============================================
        self.stdout.write("\n🔍 Creando solicitudes de clases...")
        
        # Limpiar solicitudes duplicadas
        duplicates_solicitudes = SolicitudClase.objects.values('solicitante', 'titulo').annotate(
            count=Count('id')
        ).filter(count__gt=1)
        
        for dup in duplicates_solicitudes:
            solicitudes_dup = SolicitudClase.objects.filter(
                solicitante=dup['solicitante'],
                titulo=dup['titulo']
            ).order_by('-fecha_publicacion')
            # Mantener la primera (más reciente), eliminar el resto
            to_delete = solicitudes_dup[1:]
            for solicitud in to_delete:
                solicitud.delete()
            self.stdout.write(self.style.WARNING(f"  🧹 Limpiadas solicitudes duplicadas: {dup['titulo'][:40]}..."))
        
        solicitudes_data = [
            {
                "solicitante": estudiantes[0],
                "titulo": "Busco profesor de Cálculo II urgente",
                "descripcion": "Tengo certamen la próxima semana y necesito ayuda con integrales múltiples y series. Disponibilidad inmediata, presencial o online.",
                "ramo": ramos[2],
            },
            {
                "solicitante": estudiantes[1],
                "titulo": "Necesito clases de Programación para examen",
                "descripcion": "Busco profesor que me ayude a preparar el examen de Programación (Python). Necesito reforzar recursión y POO principalmente.",
                "ramo": ramos[12],
            },
            {
                "solicitante": estudiantes[2],
                "titulo": "Ayuda con proyecto de Bases de Datos",
                "descripcion": "Necesito apoyo para diseñar el modelo ER de mi proyecto final. Incluye normalización y optimización de consultas SQL.",
                "ramo": ramos[15],
            },
            {
                "solicitante": estudiantes[3],
                "titulo": "Clases de Algoritmos - Programación Dinámica",
                "descripcion": "Estoy con problemas en programación dinámica y algoritmos greedy. Busco alguien con experiencia en competencias de programación.",
                "ramo": ramos[14],
            },
            {
                "solicitante": estudiantes[4],
                "titulo": "Física II - Electricidad y Magnetismo",
                "descripcion": "Necesito clases de la parte de electricidad de Física II. Leyes de Kirchhoff, circuitos RC, RL, RLC. Preferiblemente presencial.",
                "ramo": ramos[9],
            },
            {
                "solicitante": estudiantes[5],
                "titulo": "Álgebra Lineal - Espacios Vectoriales",
                "descripcion": "Me cuesta mucho entender espacios vectoriales, transformaciones lineales y valores propios. Busco explicaciones claras con ejemplos.",
                "ramo": ramos[0],
            },
            {
                "solicitante": estudiantes[6],
                "titulo": "Desarrollo Web - Necesito ayuda con Django",
                "descripcion": "Estoy desarrollando una aplicación con Django y tengo problemas con autenticación y manejo de sesiones. Busco mentoría técnica.",
                "ramo": ramos[21],
            },
            {
                "solicitante": estudiantes[7],
                "titulo": "Estructuras de Datos - Árboles y Grafos",
                "descripcion": "Necesito reforzar implementación de árboles binarios, AVL y algoritmos de grafos (BFS, DFS, Dijkstra). Código en Java.",
                "ramo": ramos[13],
            },
            {
                "solicitante": estudiantes[8],
                "titulo": "Ecuaciones Diferenciales - Laplace y Fourier",
                "descripcion": "Tengo problemas con transformada de Laplace y series de Fourier. Busco alguien que explique bien la teoría y aplicaciones.",
                "ramo": ramos[4],
            },
            {
                "solicitante": estudiantes[9],
                "titulo": "Machine Learning - Proyecto final",
                "descripcion": "Necesito ayuda con mi proyecto final de ML. Tengo que implementar un clasificador con redes neuronales en TensorFlow.",
                "ramo": ramos[20],
            },
        ]

        for data in solicitudes_data:
            solicitud, created = SolicitudClase.objects.update_or_create(
                solicitante=data["solicitante"],
                titulo=data["titulo"],
                defaults={
                    "descripcion": data["descripcion"],
                    "ramo": data["ramo"]
                }
            )
            status = "✅ Creada" if created else "♻️  Actualizada"
            self.stdout.write(f"  {status}: {data['titulo'][:50]}... por {data['solicitante'].user.username}")

        # ============================================
        # 9. CREAR USUARIOS QUE DAN Y SOLICITAN CLASES
        # ============================================
        self.stdout.write("\n🔄 Creando usuarios que ofrecen Y solicitan clases...")

        # Profesores que también solicitan
        solicitudes_profesores = [
            {
                "solicitante": profesores[2],
                "titulo": "Busco ayuda con Machine Learning avanzado",
                "descripcion": "Quiero aprender sobre redes neuronales profundas y transformers. Busco alguien con experiencia en investigación de ML.",
                "ramo": ramos[20],
            },
            {
                "solicitante": profesores[0],
                "titulo": "Necesito clases de Desarrollo Web moderno",
                "descripcion": "Quiero aprender React y frameworks modernos para crear aplicaciones educativas. Tengo conocimientos básicos de HTML/CSS.",
                "ramo": ramos[21],
            },
            {
                "solicitante": profesores[4],
                "titulo": "Ayuda con Sistemas Operativos",
                "descripcion": "Necesito reforzar conceptos de concurrencia y sincronización para un proyecto. Threads, semáforos, deadlocks.",
                "ramo": ramos[17],
            },
        ]

        for data in solicitudes_profesores:
            solicitud, created = SolicitudClase.objects.update_or_create(
                solicitante=data["solicitante"],
                titulo=data["titulo"],
                defaults={
                    "descripcion": data["descripcion"],
                    "ramo": data["ramo"]
                }
            )
            status = "✅ Creada" if created else "♻️  Actualizada"
            self.stdout.write(f"  {status}: Profesor solicita - {data['titulo'][:40]}... por {data['solicitante'].user.username}")

        # Estudiantes que también ofrecen
        ofertas_estudiantes = [
            {
                "profesor": estudiantes[0],
                "titulo": "Clases de Programación básica - Ayudante certificado",
                "descripcion": "Soy ayudante del curso de Programación. Ofrezco clases de reforzamiento en Python, ideal para principiantes. Métodos didácticos y paciencia.",
                "ramos": [ramos[12]],
            },
            {
                "profesor": estudiantes[3],
                "titulo": "Algoritmos y Estructuras de Datos - Competitiva",
                "descripcion": "Tengo experiencia en competencias de programación (ACM-ICPC). Te ayudo con algoritmos complejos y estructuras de datos avanzadas.",
                "ramos": [ramos[13], ramos[14]],
            },
            {
                "profesor": estudiantes[5],
                "titulo": "Física básica - Estudiante de Ingeniería",
                "descripcion": "Estudio Ingeniería Civil en Computación y tengo buen manejo de Física I. Puedo ayudarte con mecánica clásica y cinemática.",
                "ramos": [ramos[8]],
            },
            {
                "profesor": estudiantes[8],
                "titulo": "Cálculo y Álgebra - Estudiante avanzado",
                "descripcion": "Curso 4to año de Ingeniería Matemática. Ofrezco clases de Cálculo I, II y Álgebra Lineal con enfoque en teoría y ejercicios.",
                "ramos": [ramos[0], ramos[1], ramos[2]],
            },
        ]

        ofertas_estudiantes_creadas = []
        for data in ofertas_estudiantes:
            oferta, created = OfertaClase.objects.update_or_create(
                profesor=data["profesor"],
                titulo=data["titulo"],
                defaults={"descripcion": data["descripcion"]}
            )
            oferta.ramos.set(data["ramos"])
            ofertas_estudiantes_creadas.append(oferta)
            status = "✅ Creada" if created else "♻️  Actualizada"
            self.stdout.write(f"  {status}: Estudiante ofrece - {data['titulo'][:40]}... por {data['profesor'].user.username}")

        # Asignar horarios a ofertas de estudiantes
        self.stdout.write("\n⏰ Asignando horarios a ofertas de estudiantes...")
        for oferta in ofertas_estudiantes_creadas:
            # Eliminar horarios anteriores
            oferta.horarios.all().delete()
            
            # Asignar entre 2 y 3 horarios
            num_horarios = random.randint(2, 3)
            dias_usados = set()
            
            for _ in range(num_horarios):
                dias_disponibles = [d for d in DiaSemana.values if d not in dias_usados]
                if not dias_disponibles:
                    break
                    
                dia = random.choice(dias_disponibles)
                dias_usados.add(dia)
                
                hora_inicio, hora_fin = random.choice(horarios_disponibles)
                
                HorarioOfertado.objects.create(
                    oferta=oferta,
                    dia=dia,
                    hora_inicio=hora_inicio,
                    hora_fin=hora_fin,
                    cupos_totales=random.randint(1, 3)
                )
            
            dia_nombres = [DiaSemana(d).label for d in sorted(dias_usados)]
            self.stdout.write(f"  ✅ Asignados {len(dias_usados)} horarios a '{oferta.titulo[:40]}...' ({', '.join(dia_nombres)})")

        # ============================================
        # RESUMEN FINAL
        # ============================================
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("✅ POBLACIÓN COMPLETADA"))
        self.stdout.write("="*60)
        self.stdout.write(f"📚 Carreras en BD: {Carrera.objects.count()}")
        self.stdout.write(f"📖 Ramos en BD: {Ramo.objects.count()}")
        self.stdout.write(f"👥 Usuarios totales: {User.objects.count()}")
        self.stdout.write(f"   - Profesores: {len(profesores)}")
        self.stdout.write(f"   - Estudiantes: {len(estudiantes)}")
        self.stdout.write(f"💼 Ofertas en BD: {OfertaClase.objects.count()}")
        self.stdout.write(f"🔍 Solicitudes en BD: {SolicitudClase.objects.count()}")
        self.stdout.write(f"📝 Ramos cursados asignados: {PerfilRamo.objects.count()}")
        self.stdout.write(f"⏰ Horarios ofertados: {HorarioOfertado.objects.count()}")
        self.stdout.write("\n🎉 ¡Listo! Puedes iniciar sesión con:")
        self.stdout.write(self.style.SUCCESS("   Username: profProgramacion | Password: password123"))
        self.stdout.write(self.style.SUCCESS("   Username: juan_perez | Password: password123"))
        self.stdout.write("="*60)
