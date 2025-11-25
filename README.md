# Dashboard Metas Sanitarias Ley 20.707

## Descripción

Este proyecto es un dashboard interactivo desarrollado con Streamlit para el monitoreo de las Metas Sanitarias según la Ley 20.707. La aplicación permite visualizar, analizar y simular el cumplimiento de diversas metas sanitarias a través de datos obtenidos desde una hoja de cálculo pública de Google Sheets.

## Características

- Selección dinámica de Unidades de Desempeño para analizar indicadores específicos.
- Visualización detallada de cada indicador con gráficos de evolución mensual.
- Simulación editable de valores mensuales para evaluar distintos escenarios de cumplimiento.
- Comparación visual de indicadores mediante gráficos de barras y líneas.
- Estadísticas detalladas con métricas como promedio, mínimo, máximo y desviación estándar.
- Persistencia de datos editados durante la sesión.
- Calculadora para simular porcentajes referenciales.
- Interfaz intuitiva y layout amplio (wide) para mejor experiencia de usuario.
- Barra lateral con información del proyecto y funcionalidades.

## Instalación

1. Clonar este repositorio o descargar los archivos.
2. Crear un entorno virtual (opcional, pero recomendado):

```bash
python -m venv venv
```

3. Activar el entorno virtual:

- En Windows:

```bash
venv\Scripts\activate
```

- En macOS/Linux:

```bash
source venv/bin/activate
```

4. Instalar las dependencias desde el archivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

## Uso

Para ejecutar la aplicación, usar el siguiente comando en la terminal:

```bash
streamlit run visualizasimula.py
```

Esto abrirá una ventana del navegador con el dashboard interactivo.

## Fuente de Datos

Los datos se cargan dinámicamente desde la siguiente hoja de cálculo pública en Google Sheets:

[https://docs.google.com/spreadsheets/d/e/2PACX-1vQ7yKDhmdK-Hz4Qcr_wpQo9u4Vf6arzrcTEhqujrJUD59Lu9haFKyLQQDdUfgBijB7clgYHpp5x28SZ/pub?gid=304183817&single=true&output=csv](https://docs.google.com/spreadsheets/d/e/2PACX-1vQ7yKDhmdK-Hz4Qcr_wpQo9u4Vf6arzrcTEhqujrJUD59Lu9haFKyLQQDdUfgBijB7clgYHpp5x28SZ/pub?gid=304183817&single=true&output=csv)

## Dependencias

El proyecto utiliza las siguientes librerías, listadas también en `requirements.txt`:

- streamlit
- pandas
- plotly
- requests

## Versión

v4.1 - Dashboard Interactivo

## Información Adicional

En la barra lateral de la aplicación se muestra un resumen de las funcionalidades presentes y detalles del proyecto.

## Licencia

Este proyecto no posee licencia específica por el momento. Consulte con el autor para más detalles.
