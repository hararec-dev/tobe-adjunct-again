#!/usr/bin/env python3

import logging
from src.modules.fciencias_scraper import FcienciasScraper

logging.basicConfig(level=logging.INFO)

def diagnose():
    scraper = FcienciasScraper(headless=False)
    scraper.setup_driver()
    
    try:
        # Solo probar login y obtener asignaturas
        if scraper.login():
            subjects = scraper.get_subjects()
            print(f"Login exitoso")
            print(f"Asignaturas encontradas: {len(subjects)}")
            
            # Probar una asignatura específica
            if subjects:
                test_subject = subjects[0]
                print(f"Probando asignatura: {test_subject['name']}")
                
                professors = scraper.get_professors_from_subject(test_subject['url'], test_subject['name'])
                print(f"Profesores encontrados en {test_subject['name']}: {len(professors)}")
                
                for prof in professors[:5]:  # Mostrar primeros 5
                    print(f"  - {prof['name']}: {prof['url']}")
        else:
            print("Error en login")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        scraper.driver.quit()

if __name__ == "__main__":
    diagnose()