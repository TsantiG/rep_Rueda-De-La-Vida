# 🚀 Proyecto RuedaVida  
🧠 **Aplicación de Ciencia de Datos con Flask**  

📌 **Descripción**  
Este proyecto es una aplicación web desarrollada en **Python y Flask** que permite analizar datos de empleados segun encuestas hechas a los mismos y visualizar información relevante por medio de graficas.  


## **Indice**

✔ **Uso de etiquetas personalizadas** (`.[NOTE].`, `.[IMPORTANT].`, etc.)  
✔ **Imágenes previsualizando el proyecto** con `![texto](URL-imagen)`.  
✔ **Código bien estructurado** con `📂 Estructura del Proyecto`.  
✔ **Guía de instalación detallada**.  
✔ **Licencia y créditos** al final.  


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
---

## 📂 Estructura del Proyecto  

ruedaVida/ │── 📁 software/ # Código del aplicativo web

│ ├── app.py # Archivo principal de Flask

│ ├── requirements.txt # Dependencias

│ ├── templates/ # HTML y plantillas

│ └── static/ # CSS, JS, imágenes


│── 📁 documentacion/ # Documentos y reportes

│ ├── manual.pdf

│ └── reporte.pdf

│
└── README.md # Este archivo


---

## 🚀 Instalación y Configuración desde la terminal de visual studio 
1️⃣ **Clonar el repositorio**  

git clone https://github.com/usuario/repo.git
cd ruedaVida

2️⃣ **Requerimientos para el devido funcionamiento desde la terminal**
Una vez clonado el proyecto ejecutar los siguientes comandos en la terminal de visual studio:

cd rueda_vida_app
  
>> pip install matplotlib
>> pip install werkzeug 
>> install reportlab 
>> pip install mysqlclient
>>  pip install flask      
>> pip install flask-mysqldb
>> pip install werkzeug
>> pip install matplotlib
>> pip install reportlab
>> pip install mysqlclient  # Solo si usas MySQL
>> pip install python-dotenv


y ejecuta el codigo mysql del archivo db.txt en cualquier cliente de mysql preferentemente en el myadmin del xampp para la creacion de la base de datos en puerto 3306

3️⃣ **Iniciar el proyecto** 

python app.py

> .[IMPORTANT].
> Asegúrate de tener Python 3.8+ instalado antes de ejecutar el proyecto.

> .[TIP].
> la documentación esta en la carpeta documentación.

### ⚙️ Funcionalidades

✅ Análisis de datos con gráficos interactivos
✅ Panel de administración
✅ Exportación de reportes en PDF y exel
✅ Autenticación de usuarios

> .[TIP].
> Puedes personalizar los gráficos en templates/dashboard.html.


### 🛠 Tecnologías Utilizadas
✅ Flask - Backend
✅ Pandas - Análisis de datos
❎ Matplotlib / Seaborn - Visualización de datos
❎ Bootstrap - Interfaz de usuario


### 📝 Contribuciones
🙆 Las contribuciones son bienvenidas. Para colaborar:

Haz un fork del repositorio.

Crea una nueva rama (git checkout -b feature-nueva).

Haz cambios y sube tus commits (git commit -m "Agregada nueva funcionalidad").

Envía un Pull Request.

> .[WARNING].
> No modifiques archivos en la rama main directamente.



## 📄 Licencia
Este proyecto está bajo la licencia MIT.

👨‍💻 Desarrollado por:

🚀 Juan David Suarez
🚀 Dayan Berrio Toro
🚀 Andres Monsalve Perez
🚀 Santiago Gallego Gutierrez

