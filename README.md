
# REEsearch_GUIapp

GUI app built with PyQt5 to find matching REE minerals from the database of webmineral.com using EPMA data


## Motivation
There are various mineral recalculation procedures for common silicate minerals given their EPMA data, but for minerals bearing REE phases, this is not the case.The website [webmineral.com](https://webmineral.com/) provides a Mineral Element Composition search box in its webpage, whereby the user can search for a given mineral by entering the wt% of elemental oxides (three at a time) and the site provides the matching mineral name list. This process can be tedious if there are more than three elemental oxides in your EPMA data. You will have to search using different combinations of the elements to finally narrow down the mineral. The desktop application REEsearch was developed in order to ease this process A web application with named REE-search-webapp is also available and is hosted at https://github.com/soorajgeo/REE_search-webapp

## Usage and methodology
This application can be used if your EPMA data contains atleast one of the REE bearing elements (La to Lu, Y and Sc) in weight percent oxides. The database for REE bearing minerals were created by webscraping [webmineral.com](https://webmineral.com/) using the [beautiful-soup](https://beautiful-soup-4.readthedocs.io/en/latest/) python library.  The data is stored as csv file (REE_data.csv) and is available for download along with the .exe files. This csv file should not be moved or modified, since the application uses this file as its database. But the user can copy the file to any other folder /location.
The user can upload a csv file containing the elemental oxide weight percent data (usually EPMA data) in columns and the point analysis as rows. Make sure the total for each point analysis is close to 100%. The application also displays the demo csv format in its first window for reference. 

The application uses simple vector algebra method known as cosine similarity (https://en.wikipedia.org/wiki/Cosine_similarity) to identify the minerals from the database. First it converts the user data into vectors (vectors can be any dimension- this is why you can search for minerals with any number of elements in its composition) and compare against the REE database (REE_data.csv) and displays the result which the user can download as csv. The user can also click any rows of the result window to compare their data with the REE database. See the below gif to see how the application runs.

## Python libraries used

- Scikit-learn for performing pairwise cosine similarity search
- PyQT5 for designing the application interface
- numpy and pandas for data wrangling


## Demo
![](https://github.com/soorajgeo/REE_search_GUIapp/assets/51475605/252dc08a-df73-43d2-b75e-48700b513a28)




## Run Locally

Clone the project

```bash
  git clone https://github.com/soorajgeo/REE_search_GUIapp.git
```

Go to the project directory

```bash
  cd REE_search_GUIapp
```

Install dependencies

```bash
  pip install -r requirements.txt
```

run the ree.py python file

```bash
  python ree.py
```


## Installation

Click the link to download the executables from my 
[google drive link](https://drive.google.com/drive/folders/1QIPYpVjohNKigkuuaSK9CFTLAX67scfi?usp=drive_link)
    
