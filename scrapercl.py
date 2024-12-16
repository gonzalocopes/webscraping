import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

# Configuración del WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# Abrir la página web
driver.get("http://scw.pjn.gov.ar/scw/home.seam")

# Esperar hasta que cargue la página
time.sleep(3)

# Configuración de espera explícita
wait = WebDriverWait(driver, 10)

# Cambiar de pestaña "Por Expediente" a "Por Parte"
try:
    # Verificar si estamos en la sección 'Por Expediente'
    if driver.find_element(By.CSS_SELECTOR, "#formPublica\\:porExpediente\\:header\\:active"):
        print("Estamos en la sección 'Por Expediente'. Ahora cambiamos a 'Por Parte'.")
        
        # Hacer clic en la pestaña 'Por Parte'
        tab_by_part = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#formPublica\\:porParte\\:header\\:inactive > span")))
        tab_by_part.click()
        print("Sección cambiada a 'Por Parte'.")
except Exception as e:
    print(f"Error al verificar la sección 'Por Expediente' o hacer clic en 'Por Parte': {e}")

# Esperar un poco para que la sección 'Por Parte' se cargue correctamente
time.sleep(2)

# Selección de la jurisdicción
try:
    # Esperar que el dropdown de jurisdicción sea visible
    jurisdiction_dropdown = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "formPublica:camaraPartes"))
    )

    # Desplazar el dropdown a la vista
    driver.execute_script("arguments[0].scrollIntoView(true);", jurisdiction_dropdown)

    # Hacer clic en el dropdown para desplegar las opciones
    jurisdiction_dropdown.click()

    # Esperar que las opciones sean visibles
    time.sleep(1)  # Esperar para que el dropdown se despliegue

    # Intentar hacer clic en la opción "10" (COM - Cámara Nacional de Apelaciones en lo Comercial)
    jurisdiction_option = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//option[@value='10']"))
    )
    jurisdiction_option.click()
    print("Jurisdicción seleccionada: COM - Cámara Nacional de Apelaciones en lo Comercial.")

except Exception as e:
    try:
        # Usar JavaScript para seleccionar la opción si el clic falla
        driver.execute_script("arguments[0].value = '10';", jurisdiction_dropdown)
        print("Jurisdicción seleccionada mediante JavaScript.")
    except Exception as js_error:
        print(f"Error al intentar seleccionar la jurisdicción con JavaScript: {js_error}")

# Escribir "RESIDUOS" en el campo de parte
input_residuos = driver.find_element(By.ID, "formPublica:nomIntervParte")
input_residuos.clear()
input_residuos.send_keys("RESIDUOS")

# Esperar a que resuelvas el CAPTCHA manualmente
print("Por favor, resuelve el CAPTCHA y luego presiona Enter en la terminal para continuar.")
input("Presiona Enter cuando hayas resuelto el CAPTCHA...")

# Hacer clic en el botón de consulta
consult_button = driver.find_element(By.ID, "formPublica:buscarPorParteButton")
consult_button.click()

# Esperar a que se carguen los resultados (ajustar el tiempo de espera según la página)
time.sleep(5)

# Inicializar listas para almacenar los resultados
expedients = []
dependencies = []
headlines = []
situations = []
relevant_dates = []

# Extraer los resultados de la tabla
rows = driver.find_elements(By.CSS_SELECTOR, "#j_idt118\\:j_idt119\\:dataTable > tbody > tr")

for row in rows:
    try:
        # Extraer la información de cada celda
        expediente = row.find_element(By.XPATH, ".//td[1]").text
        dependencia = row.find_element(By.XPATH, ".//td[2]").text
        caratula = row.find_element(By.XPATH, ".//td[3]").text
        situacion = row.find_element(By.XPATH, ".//td[4]").text
        fecha_relevante = row.find_element(By.XPATH, ".//td[5]").text
        
        # Agregar los datos a las listas
        expedients.append(expediente)
        dependencies.append(dependencia)
        headlines.append(caratula)
        situations.append(situacion)
        relevant_dates.append(fecha_relevante)
        
    except Exception as e:
        print(f"Error al extraer una fila: {e}")

# Almacenar los datos en un DataFrame de pandas y luego guardarlos en un archivo Excel
df = pd.DataFrame({
    'Expediente': expedients,
    'Dependencia': dependencies,
    'Carátula': headlines,
    'Situación': situations,
    'Últ. Act.': relevant_dates
})

# Guardar los datos en un archivo Excel
df.to_excel("resultados_scraping.xlsx", index=False)

# Imprimir mensaje de confirmación
print("¡Excel creado con éxito!")

# Cerrar el navegador
driver.quit()
