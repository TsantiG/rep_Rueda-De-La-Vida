# 🚀 Proyecto RuedaVida  
🧠 **Aplicación de Ciencia de Datos con Flask**  

📌 **Descripción**  
Este proyecto es una aplicación web desarrollada en **Python y Flask** que permite analizar datos de empleados según encuestas hechas a los mismos y visualizar información relevante por medio de graficas he informes, tambien cuenta con toda la **documentacion** realizacda para la completacion del proyecto.  


## **Indice**

✔ **Uso de etiquetas personalizadas** (`.[NOTE].`, `.[IMPORTANT].`, etc.) 

✔ **Código bien estructurado** con `📂 Estructura del Proyecto`.  

✔ **Guía de instalación detallada**.  

✔ **Funcionalidades**.

✔ **Tecnologías Utilizadas**.

✔ **Contribuciones**.

✔ **Licencia y créditos** antes de las previsualizaciones de la pagina.

✔ **Imágenes previsualizando el proyecto** con `![texto](URL-imagen)`.  

---

## explicacion de uso de etiquetas personalizadas

> [!NOTE]
> esto es una nota.

> [!IMPORTANT]
> esto es algo que es importante.


> [!WARNING]
> etiqueta para evisar de peligro o a tener encuenta.


> [!TIP]
> etiqueta para consejos o tips.

> [!CAUTION]
> cosas a tener precausion o reglas que debes seguir.

---

## 📂 Estructura del Proyecto  

rep_Rueda-De-La-Vida/

│── 📁 rueda_vida_app/ # Código del aplicativo web

│ │── 📁 __pycache__  # cache

│ │── 📁 templates # archivos html

│ ├── 📁 static/ # CSS, JS, imágenes

│ ├── app.py # Archivo principal de Flask

│ ├── config.py # Archivo de configuracion y conexcion a la base de datos

│ └── db.txt # archivo de texto que contiene el codigo sql para crear la base de datos.


│── 📁 documentacion/ # Documentos y reportes

│ ├── INVESTIGACION CIENCIA DE DATOS.docx

│ ├── Trabajo 1 ciencia de datos.xlsm

│ ├── Trabajo_APA_Evaluacion_Emocional.docx

│ └── coquito amarillo.pptx

├── 📁 venv # carpeta de entorno de desarrollo , se creara siguiendo las instrucciones de ejecusion

└── README.md # Este archivo


---

## 🚀 Instalación y Configuración desde la terminal de visual studio 
1️⃣ **Clonar el repositorio**  


- Crea la carpeta que alvergara el repositorio.

- abrir carpeta en visual studio code.

- abrir terminal de visual studio code para ejecutar los comandos (control + ñ)

- git clone https://github.com/TsantiG/rep_Rueda-De-La-Vida.git


2️⃣ **Requerimientos para el devido funcionamiento desde la terminal**
Una vez clonado el proyecto ejecutar los siguientes comandos en la terminal de visual studio:

> [!CAUTION]
> Ejecutar todos los comandos en la terminal tal cual esta
> en la explicacion para el debido funcionamiento del programa.


cd rep_Rueda-De-La-Vida 

python -m venv venv 
> esto para crear la carpeta venv para el funcionamiento del entorno de desarrollo


cd rueda_vida_app

pip install matplotlib

pip install werkzeug 

pip install mysqlclient

pip install flask      

pip install flask-mysqldb

pip install werkzeug

pip install matplotlib

pip install reportlab

pip install python-dotenv

> esto para importar las librerias necesarioas para el proyecto.

> [!CAUTION]
> antes de inicializar el proyecto, ejecutar el codigo mysql del archivo db.txt en cualquier cliente de mysql 
> preferentemente en el myadmin del xampp para la creacion de la base de datos y utiliza el puerto 3306

3️⃣ **Iniciar el proyecto** 

python app.py

> [!IMPORTANT]
> Asegúrate de tener Python 3.8+ instalado antes de ejecutar el proyecto.

> [!TIP]
> la documentación esta en la carpeta documentación.

---

### ⚙️ Funcionalidades

✅ Análisis de datos con gráficos interactivos

✅ Panel de administración

✅ Exportación de reportes en PDF y exel

✅ Autenticación de usuarios


> [!TIP]
> Puedes personalizar los gráficos en templates/dashboard.html.

---

### 🛠 Tecnologías Utilizadas
✅ Flask - Backend

✅ Pandas - Análisis de datos

✅ Matplotlib / Seaborn - Visualización de datos

⛔ Bootstrap - Interfaz de usuario

---

### 📝 Contribuciones
🙆 Las contribuciones son bienvenidas. 

Para colaborar:

Haz un fork del repositorio.

Crea una nueva rama (git checkout -b feature-nueva).

Haz cambios y sube tus commits (git commit -m "Agregada nueva funcionalidad").

Envía un Pull Request.

> [!WARNING]
> No modifiques archivos en la rama main directamente.


---

## 📄 Licencia
Este proyecto está bajo la licencia de Apache. Explicación del por qué en la wiki.

👨‍💻 Desarrollado por:

🚀Juan David Suárez /🚀Dayan Berrio /🚀Andrés Monsalve /🚀Santiago Gallego

---




## 📸 Vista Previa  

### 🔹 Página Principal  
![Home Page](https://github.com/jdsuarez23/imagenes_rueda_vida/blob/main/inicio.png)

### 🔹 Registro Usuario
![Registro Usuario](https://github.com/jdsuarez23/imagenes_rueda_vida/blob/main/registro.png)

### 🔹 Inicio Sesión
![Inicio sesión](https://github.com/jdsuarez23/imagenes_rueda_vida/blob/main/iniciar%20sesion.png)

### 🔹 Inicio Sesión empleado
![inicio sesion empleado](https://github.com/jdsuarez23/imagenes_rueda_vida/blob/main/inicio%20sesion%20empleado.png)

### 🔹 Grafica Rueda de Vida
![grafica rueda de vida](https://github.com/jdsuarez23/imagenes_rueda_vida/blob/main/grafica%20rueda%20de%20vida.png)

### 🔹 Informe 1 Rueda de vida de empleado
![Informe rueda de vida de empleado](https://github.com/jdsuarez23/imagenes_rueda_vida/blob/main/informe_usuario_rueda_vida_2_page-0001.jpg)

### 🔹 Informe 2 Rueda de vida de empleado
![Informe rueda de vida de empleado](https://github.com/jdsuarez23/imagenes_rueda_vida/blob/main/informe_usuario_rueda_vida_2_page-0002.jpg)

### 🔹 Inicio Sesión Administrador
![Panel de Administrador](https://github.com/jdsuarez23/imagenes_rueda_vida/blob/main/panel%20administrador.png)

### 🔹 Informe 1 general de rueda de la vida
![Informe 1 general de rueda de la vida](https://github.com/jdsuarez23/imagenes_rueda_vida/blob/main/reporte_general_rueda_vida_page-0001.jpg)

### 🔹 Informe 2 general de rueda de la vida
![Informe 2 general de rueda de la vida](https://github.com/jdsuarez23/imagenes_rueda_vida/blob/main/reporte_general_rueda_vida_page-0002.jpg)

### 🔹 Informe 3 general de rueda de la vida
![Informe 3 general de rueda de la vida](https://github.com/jdsuarez23/imagenes_rueda_vida/blob/main/reporte_general_rueda_vida_page-0003.jpg)

