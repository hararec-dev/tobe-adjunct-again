#!/usr/bin/env python3

import json
import sys
import os

# Lista de materias permitidas
ALLOWED_SUBJECTS = {
    "Álgebra Superior",
    "Cálculo Diferencial e Integral",
    "Geometría Analítica",
    "Álgebra Lineal",
    "Ecuaciones Diferenciales",
    "Análisis Matemático",
    "Variable Compleja",
    "Conjuntos y Lógica",
    "Probabilidad",
    "Teoría de los Números",
    "Geometría Diferencial",
    "Lenguajes de Programación y sus Paradigmas",
    "Lógica Matemática",
    "Programación Lineal",
    "Sistemas Operativos",
    "Teoría de la Computación",
    "Teoría de la Medida",
    "Teoría de los Conjuntos",
    "Topología",
    "Complejidad Computacional",
    "Ingeniería de Software",
    "Redes de Computadoras",
    "Teoría de Redes",
    "Topología Diferencial"
}

def get_input_file():
    """Obtiene el nombre del archivo JSON por consola."""
    print("=" * 60)
    print("PROCESADOR DE ARCHIVOS JSON DE MATERIAS")
    print("=" * 60)
    
    # Verificar si se proporcionó argumento por línea de comandos
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        print(f"Archivo proporcionado por argumento: {input_file}")
    else:
        # Solicitar archivo por consola
        input_file = input("Por favor, ingrese el nombre del archivo JSON (ej: datos.json): ").strip()
    
    # Verificar que el archivo existe
    while not os.path.exists(input_file):
        print(f"Error: El archivo '{input_file}' no existe.")
        input_file = input("Ingrese el nombre del archivo JSON válido: ").strip()
    
    # Verificar extensión .json
    if not input_file.lower().endswith('.json'):
        print(f"Advertencia: El archivo '{input_file}' no tiene extensión .json")
        confirm = input("¿Continuar de todas formas? (s/n): ").strip().lower()
        if confirm != 's':
            return get_input_file()
    
    return input_file

def clean_and_filter_subjects(input_file):
    """
    Elimina duplicados, filtra 'otherSubjects' según la lista permitida,
    elimina el valor de 'subject' de 'otherSubjects', y luego elimina objetos
    donde 'subject' no está en la lista permitida.
    """
    # Leer el archivo JSON
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Estadísticas
    stats = {
        'total_items_original': len(data),
        'total_removed_all': 0,
        'subject_removed_from_otherSubjects': 0,
        'items_modified': 0,
        'items_removed_completely': 0,
        'items_removed_details': [],
        'per_item_stats': [],
        'final_item_count': 0
    }
    
    # Lista para almacenar los objetos que cumplen las condiciones
    filtered_data = []
    
    # Procesar cada objeto
    for i, item in enumerate(data):
        original_len = 0
        subject_value = item.get('subject', '')
        
        if 'otherSubjects' in item and isinstance(item['otherSubjects'], list):
            original_len = len(item['otherSubjects'])
            
            # PASO 1: Filtrar solo materias permitidas y eliminar duplicados manteniendo el orden
            seen = set()
            filtered_list = []
            
            for subject in item['otherSubjects']:
                # Verificar si está en la lista permitida
                if subject in ALLOWED_SUBJECTS:
                    # Verificar si no es duplicado
                    if subject not in seen:
                        seen.add(subject)
                        filtered_list.append(subject)
            
            # PASO 2: Eliminar el valor de 'subject' de 'otherSubjects' si está presente
            # Esto se hace después de eliminar duplicados y filtrar
            if subject_value in filtered_list:
                filtered_list.remove(subject_value)
                stats['subject_removed_from_otherSubjects'] += 1
            
            # Actualizar el campo
            item['otherSubjects'] = filtered_list
            
            # Calcular estadísticas para este item
            removed_count = original_len - len(filtered_list)
            if removed_count > 0:
                stats['total_removed_all'] += removed_count
                stats['items_modified'] += 1
            
            # Guardar estadísticas detalladas por item
            item_stats = {
                'index': i,
                'name': item.get('name', 'Sin nombre'),
                'original_count': original_len,
                'filtered_count': len(filtered_list),
                'removed_count': removed_count,
                'kept_subjects': filtered_list.copy(),
                'subject_field': subject_value,
                'is_subject_allowed': subject_value in ALLOWED_SUBJECTS,
                'subject_was_in_otherSubjects': subject_value in item['otherSubjects'] or subject_value in seen
            }
            stats['per_item_stats'].append(item_stats)
            
            # PASO 4 MODIFICADO: Verificar si el objeto debe ser eliminado completamente
            # NUEVA CONDICIÓN: Eliminar si 'subject' no está en ALLOWED_SUBJECTS
            if subject_value not in ALLOWED_SUBJECTS:
                # Este objeto será eliminado
                stats['items_removed_completely'] += 1
                stats['items_removed_details'].append({
                    'index': i,
                    'name': item.get('name', 'Sin nombre'),
                    'subject': subject_value,
                    'otherSubjects_count': len(filtered_list),
                    'reason': f"'subject' ({subject_value}) no está en lista permitida"
                })
            else:
                # Conservar el objeto (subject está en ALLOWED_SUBJECTS)
                filtered_data.append(item)
        else:
            # Si no hay 'otherSubjects' o no es una lista
            # PASO 4 MODIFICADO: Verificar si el objeto debe ser eliminado completamente
            # NUEVA CONDICIÓN: Eliminar si 'subject' no está en ALLOWED_SUBJECTS
            if subject_value not in ALLOWED_SUBJECTS:
                # Este objeto será eliminado
                stats['items_removed_completely'] += 1
                stats['items_removed_details'].append({
                    'index': i,
                    'name': item.get('name', 'Sin nombre'),
                    'subject': subject_value,
                    'otherSubjects_exists': 'otherSubjects' in item,
                    'reason': f"'subject' ({subject_value}) no está en lista permitida"
                })
            else:
                # Conservar el objeto (subject está en ALLOWED_SUBJECTS)
                filtered_data.append(item)
    
    # Actualizar el conteo final
    stats['final_item_count'] = len(filtered_data)
    
    # Generar nombre para el archivo de salida
    base_name = os.path.splitext(input_file)[0]
    output_file = f"{base_name}_procesado.json"
    
    # Guardar el archivo JSON modificado
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(filtered_data, f, ensure_ascii=False, indent=4)
    
    print(f"\n✓ Archivo procesado exitosamente.")
    print(f"✓ Guardado como: {output_file}")
    
    return filtered_data, stats, output_file

def show_statistics(stats, data):
    """Muestra estadísticas detalladas del procesamiento."""
    print("\n" + "="*70)
    print("ESTADÍSTICAS DEL PROCESAMIENTO")
    print("="*70)
    print(f"Total de objetos originales: {stats['total_items_original']}")
    print(f"Objetos en archivo final: {stats['final_item_count']}")
    print(f"Objetos eliminados completamente: {stats['items_removed_completely']}")
    print(f"Objetos modificados (filtrados): {stats['items_modified']}")
    print(f"Veces que 'subject' fue eliminado de 'otherSubjects': {stats['subject_removed_from_otherSubjects']}")
    print(f"Elementos eliminados de 'otherSubjects' (duplicados + no permitidos): {stats['total_removed_all']}")
    
    # Mostrar detalles de objetos eliminados completamente
    if stats['items_removed_details']:
        print("\n" + "-"*70)
        print("OBJETOS ELIMINADOS COMPLETAMENTE (subject no permitido):")
        print("-"*70)
        for removed in stats['items_removed_details']:
            print(f"\n• {removed['name']}:")
            print(f"  Materia principal ('subject'): {removed['subject']}")
            if 'otherSubjects_count' in removed:
                print(f"  Elementos en 'otherSubjects' después del filtrado: {removed['otherSubjects_count']}")
            print(f"  Razón: {removed['reason']}")
    
    # Resumen de objetos conservados
    print("\n" + "-"*70)
    print("RESUMEN DE OBJETOS CONSERVADOS:")
    print("-"*70)
    
    # Contar cuántos objetos tienen 'subject' en ALLOWED_SUBJECTS
    subject_allowed_count = sum(1 for item in data if item.get('subject', '') in ALLOWED_SUBJECTS)
    print(f"Objetos con 'subject' en lista permitida: {subject_allowed_count}/{len(data)}")
    
    # Contar cuántos objetos tienen 'otherSubjects' no vacío
    other_subjects_non_empty = sum(1 for item in data 
                                  if 'otherSubjects' in item and 
                                  isinstance(item['otherSubjects'], list) and 
                                  len(item['otherSubjects']) > 0)
    print(f"Objetos con 'otherSubjects' no vacío: {other_subjects_non_empty}/{len(data)}")
    
    # Mostrar algunos ejemplos de objetos conservados
    if data:
        print("\nEjemplos de objetos conservados:")
        print("-"*40)
        for i, item in enumerate(data[:3]):  # Mostrar primeros 3 como ejemplo
            subject = item.get('subject', '')
            other_len = len(item.get('otherSubjects', []))
            print(f"{i+1}. {item.get('name', 'Sin nombre')}")
            print(f"   Subject: {subject} ({'Permitido' if subject in ALLOWED_SUBJECTS else 'No permitido'})")
            print(f"   OtherSubjects: {other_len} materia(s)")
            if other_len > 0:
                print(f"   Materias: {', '.join(item['otherSubjects'][:3])}" + 
                      ("..." if len(item['otherSubjects']) > 3 else ""))
            print()
    else:
        print("\n¡ADVERTENCIA: No hay objetos conservados en el archivo final!")

def generate_detailed_report(data, stats, output_file_base):
    """Genera reportes detallados en archivos de texto."""
    # Reporte de frecuencia de materias
    subject_frequency_other = {}
    subject_frequency_main = {}
    
    for item in data:
        # Frecuencia en 'otherSubjects'
        if 'otherSubjects' in item and isinstance(item['otherSubjects'], list):
            for subject in item['otherSubjects']:
                if subject in ALLOWED_SUBJECTS:
                    subject_frequency_other[subject] = subject_frequency_other.get(subject, 0) + 1
        
        # Frecuencia en 'subject'
        subject = item.get('subject', '')
        if subject in ALLOWED_SUBJECTS:
            subject_frequency_main[subject] = subject_frequency_main.get(subject, 0) + 1
    
    # Ordenar por frecuencia
    sorted_freq_other = sorted(subject_frequency_other.items(), key=lambda x: x[1], reverse=True)
    sorted_freq_main = sorted(subject_frequency_main.items(), key=lambda x: x[1], reverse=True)
    
    # Generar reporte 1: Frecuencia de materias
    report_file = f"{output_file_base}_reporte_frecuencia.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("REPORTE DE FRECUENCIA DE MATERIAS\n")
        f.write("="*70 + "\n\n")
        f.write(f"Archivo procesado: {output_file_base}.json\n")
        f.write(f"Total de objetos: {len(data)}\n")
        f.write(f"Fecha de generación: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("FRECUENCIA EN CAMPO 'subject' (materia principal):\n")
        f.write("-"*50 + "\n")
        for subject, count in sorted_freq_main:
            f.write(f"{subject}: {count} ocurrencia(s)\n")
        
        f.write(f"\nTotal de materias únicas en 'subject': {len(sorted_freq_main)}\n\n")
        
        f.write("FRECUENCIA EN CAMPO 'otherSubjects':\n")
        f.write("-"*50 + "\n")
        for subject, count in sorted_freq_other:
            f.write(f"{subject}: {count} ocurrencia(s)\n")
        
        f.write(f"\nTotal de materias únicas en 'otherSubjects': {len(sorted_freq_other)}\n\n")
        
        # Materias que no aparecieron
        missing_main = ALLOWED_SUBJECTS - set(subject_frequency_main.keys())
        missing_other = ALLOWED_SUBJECTS - set(subject_frequency_other.keys())
        
        if missing_main:
            f.write("Materias permitidas que NO aparecieron en 'subject':\n")
            f.write("-"*50 + "\n")
            for subject in sorted(missing_main):
                f.write(f"{subject}\n")
            f.write("\n")
        
        if missing_other:
            f.write("Materias permitidas que NO aparecieron en 'otherSubjects':\n")
            f.write("-"*50 + "\n")
            for subject in sorted(missing_other):
                f.write(f"{subject}\n")
    
    print(f"✓ Reporte de frecuencia generado: {report_file}")
    
    # Generar reporte 2: Detalles del procesamiento
    stats_file = f"{output_file_base}_estadisticas.txt"
    with open(stats_file, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("ESTADÍSTICAS DETALLADAS DEL PROCESAMIENTO\n")
        f.write("="*70 + "\n\n")
        
        f.write(f"Total objetos originales: {stats['total_items_original']}\n")
        f.write(f"Objetos en archivo final: {stats['final_item_count']}\n")
        f.write(f"Objetos eliminados completamente: {stats['items_removed_completely']}\n")
        f.write(f"Objetos modificados: {stats['items_modified']}\n")
        f.write(f"'subject' eliminado de 'otherSubjects': {stats['subject_removed_from_otherSubjects']} veces\n")
        f.write(f"Elementos eliminados de 'otherSubjects': {stats['total_removed_all']}\n\n")
        
        if stats['items_removed_details']:
            f.write("OBJETOS ELIMINADOS (subject no permitido):\n")
            f.write("-"*50 + "\n")
            for removed in stats['items_removed_details']:
                f.write(f"• {removed['name']}\n")
                f.write(f"  Subject: {removed['subject']}\n")
                f.write(f"  Razón: {removed['reason']}\n")
                if 'otherSubjects_count' in removed:
                    f.write(f"  OtherSubjects después del filtrado: {removed['otherSubjects_count']} elementos\n")
                f.write("\n")
    
    print(f"✓ Reporte de estadísticas generado: {stats_file}")
    
    return report_file, stats_file

def main():
    """Función principal del programa."""
    try:
        # 1. Obtener archivo de entrada
        input_file = get_input_file()
        
        # 2. Procesar el archivo
        print(f"\nProcesando archivo: {input_file}")
        print("=" * 40)
        
        cleaned_data, statistics, output_file = clean_and_filter_subjects(input_file)
        
        # 3. Mostrar estadísticas
        show_statistics(statistics, cleaned_data)
        
        # 4. Generar reportes
        output_base = os.path.splitext(output_file)[0]
        report_files = generate_detailed_report(cleaned_data, statistics, output_base)
        
        # 5. Resumen final
        print("\n" + "="*70)
        print("RESUMEN FINAL DEL PROCESAMIENTO")
        print("="*70)
        print("Pasos realizados:")
        print("  1. ✓ Eliminación de duplicados en 'otherSubjects'")
        print("  2. ✓ Filtrado de materias no permitidas (lista de 24 materias)")
        print("  3. ✓ Eliminación del valor de 'subject' de 'otherSubjects'")
        print("  4. ✓ Eliminación de objetos con 'subject' no permitido (independientemente de 'otherSubjects')")
        print(f"\nArchivos generados:")
        print(f"  • {output_file} (datos procesados)")
        print(f"  • {report_files[0]} (reporte de frecuencia)")
        print(f"  • {report_files[1]} (estadísticas detalladas)")
        print("="*70)
        
        # Preguntar si desea ver una vista previa
        if cleaned_data:
            preview = input("\n¿Desea ver una vista previa del archivo procesado? (s/n): ").strip().lower()
            if preview == 's':
                print("\nVISTA PREVIA (primeros 2 objetos):")
                print("-"*40)
                for i, item in enumerate(cleaned_data[:2]):
                    print(f"\nObjeto {i+1}:")
                    print(f"  Nombre: {item.get('name')}")
                    print(f"  Subject: {item.get('subject')} ({'Permitido' if item.get('subject') in ALLOWED_SUBJECTS else 'No permitido'})")
                    print(f"  OtherSubjects ({len(item.get('otherSubjects', []))}):")
                    for subject in item.get('otherSubjects', []):
                        print(f"    - {subject}")
        
        print("\n¡Proceso completado exitosamente!")
        
    except FileNotFoundError:
        print("Error: Archivo no encontrado.")
    except json.JSONDecodeError:
        print("Error: El archivo no tiene formato JSON válido.")
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()