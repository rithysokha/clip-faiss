## Installation
1. Create python virtual environment
2. Install the required packages
```commandline
pip install -r requirements.txt
```

## Usage

### Download images
You need a csv file that contains name, image url, sku.
and store it in ./cave 
```commandline
python download.py
```
This code will crop out human face and only focus on product.
### Create index
```commandline
python index.py
```

An index file named `index.faiss` will be created in the `static` directory.
A mapping file named `image_paths.json` will be created in the `static` directory.

### Search Web App
```commandline
python serve.py
```
The application will be hosted at `http://localhost:5000/`.

You can input natural language to search or input image to search for similar images

## Files
```commandline
clip-faiss/
├── static/                    # Web app static files                
│   ├── images/                      
│   │   └──XXXXXXX             # SKU numbers
│   │       └──blablabla.jpg  
│   ├── app.js 
│   ├── image_paths.json       # mapping file (demo)
│   ├── index.faiss            # index file (demo)
│   └── styles.css       
├── templates/                 # HTML templates
│   └── index.html             
├── app.py                     # Run CLI App
├── index.py                   # Indexing
├── download.py                # Run image downloading
├── README.md                  # This file
├── requirements.txt           # Requirements file
└── serve.py                   # Run Web App
```

## License
This project is licensed under the MIT License. Feel free to use, modify, and distribute the code as per the terms of the license.
