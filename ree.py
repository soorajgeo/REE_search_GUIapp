from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QTableView, QMessageBox, QPushButton, QVBoxLayout, QTableWidgetItem, QApplication, QStyleFactory, QProgressBar, QStyle
import sys, os
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from PyQt5.QtCore import QThread, pyqtSignal, QAbstractTableModel, Qt

# base_dir = os.path.dirname(__file__)

class pandasModel(QAbstractTableModel):
  def __init__(self,data):
    super().__init__()
    self._data = data
    
  def rowCount(self, parent=None):
    return self._data.shape[0]
  
  def columnCount(self, parent=None):
    return self._data.shape[1]
  
  def data(self, index, role=Qt.DisplayRole):
    if index.isValid():
      if role == Qt.DisplayRole:
        return str(self._data.iloc[index.row(), index.column()])
    return None
      
  def headerData(self, col, orientation, role):
    if orientation == Qt.Horizontal and role == Qt.DisplayRole:
      return self._data.columns[col]
    return None


class Window3(QtWidgets.QWidget):
  def __init__(self,db_table,label):
    super().__init__()
    self.setWindowIcon(QtGui.QIcon('crystal.ico'))
    self.setWindowTitle("Webmineral database")
    self.db_table = db_table
    self.label = label
    self.resize(500,500)

    self.label3 = QtWidgets.QLabel(self)
    text = "Compositions for the similar minerals from webmineral database for point {}".format(self.label)
    self.label3.setText(text)
    label3_font = QtGui.QFont("Times", 10, QtGui.QFont.Bold)
    self.label3.setFont(label3_font)

    self.table2 = QTableView(self)
    self.model2 = pandasModel(self.db_table)
    self.table2.setModel(self.model2)

    layout3 = QVBoxLayout(self)
    layout3.addWidget(self.label3)
    layout3.addWidget(self.table2)
    
    self.show()
    
  

class Window2(QtWidgets.QWidget):
  

  def __init__(self, result_df, ree_df):
    super().__init__()
    self.setWindowIcon(QtGui.QIcon('crystal.ico'))
    
    self.setWindowTitle("Result window")
    self.result_df = result_df
    self.ree_df = ree_df
    self.font = QtGui.QFont()
    self.font.setFamily("Arial Black")
    self.font.setPointSize(10)
    self.resize(800,600)

    self.label2 = QtWidgets.QLabel(self)
    self.label2.setText("Please click any row to compare with the webmineral database")
    label2_font = QtGui.QFont("Times", 10, QtGui.QFont.Bold)
    self.label2.setFont(label2_font)

    self.table_view = QTableView(self)
    self.model = pandasModel(self.result_df)
    self.table_view.setModel(self.model)
    
    self.table_view.clicked.connect(self.viewClicked)
    self.table_view.setSelectionBehavior(QTableView.SelectRows)

    
    self.button3 = QPushButton(self)
    self.button3.setText("Click to download")
    self.button3.setFont(self.font)
    self.button3.clicked.connect(self.download)
   
    layout2 = QVBoxLayout(self)
    layout2.addWidget(self.label2)
    layout2.addWidget(self.table_view)
    layout2.addWidget(self.button3)
    

  def download(self):
    file, _ = QFileDialog.getSaveFileName(self.button3,"Save File", filter='*.csv')
    if file == '':
      pass
    else:
      self.result_df.to_csv(file, index=False)

  def viewClicked(self, clickedIndex):
    row=clickedIndex.row()
    model=clickedIndex.model()
    label = model._data.iloc[row][0]
    mineral3 = self.ree_df.loc[self.result_df.iloc[row][-1]]
    mineral2 = self.ree_df.loc[self.result_df.iloc[row][-2]]
    mineral1 = self.ree_df.loc[self.result_df.iloc[row][-3]]
    result = pd.concat([mineral1, mineral2, mineral3], axis=1)
    result = result.loc[~(result==0).all(axis=1)].reset_index()
    result.rename(columns={'index':'Element oxide'}, inplace=True)
    
    
    self.window3 = Window3(result,label)

    
class WorkerThread(QThread):

  update = pyqtSignal(object, object)
  progress = pyqtSignal(int)

  def __init__(self,df):
    super().__init__()
    self.df = df
    
    

  def run(self):
    points = self.df.iloc[:,0]
    
    
    self.df.fillna(0, inplace=True)
    
    concatenated_df = pd.read_csv('REE_data.csv')
    
    self.ree_df = concatenated_df.copy()
    concatenated_df = concatenated_df.drop(columns='Minerals')
    
    
    # Get the list of element columns from df_minerals
    element_columns = concatenated_df.columns


    # Create missing element columns in df_user if they don't exist
    for element in element_columns:
      if element not in self.df.columns:
        self.df[element] = 0

    # Reorder the columns in df_user to match the order in df_minerals
    self.df = self.df[concatenated_df.columns]
    
        
    # Calculate cosine similarity between the numpy array and each row in the DataFrame
    sim_1, sim_2, sim_3 = [], [], []
    ree_array = concatenated_df.to_numpy()

    count = 0
    for i in range(self.df.shape[0]):
      array = self.df.iloc[i,:].values.ravel()
      
      sim_values = []
      for j in range(ree_array.shape[0]):
          
        similarities = cosine_similarity([ree_array[j]], [array])[0][0]
        sim_values.append(similarities.item())
      

      series = pd.Series(sim_values)
      # Find the indices of the three most similar minerals
      most_similar_mineral_indices = series.nlargest(3).index

      # Get the names of the three most similar minerals
      most_similar_minerals = self.ree_df.loc[most_similar_mineral_indices, 'Minerals'].tolist()

      
      sim_1.append(most_similar_minerals[0])
      sim_2.append(most_similar_minerals[1])
      sim_3.append(most_similar_minerals[2])
      count = int((i+1) * 100/self.df.shape[0])
      
      self.progress.emit(count)

      
    self.df['Most similar'] = sim_1
    self.df['2nd most similar'] = sim_2
    self.df['3rd most similar'] = sim_3
    self.df = self.df.loc[:, (self.df != 0).any(axis=0)]
    self.df.insert(0,'Points',points)
    
    self.ree_df.set_index('Minerals', drop=True, inplace=True)
    self.df.reset_index(drop=True,inplace=True)
    self.result_df = self.df

    self.update.emit(self.result_df, self.ree_df)
    
    


class Window1(QtWidgets.QWidget):
  def __init__(self):
    super().__init__()
    self.setWindowIcon(QtGui.QIcon('crystal.ico'))
    self.setWindowTitle("REE search")
    self.resize(900,600)
    self.label1 = QtWidgets.QLabel(self)
    self.label1.setText("Please upload csv file of the following format (Enter 0 or leave blank for no data)")
    label1_font = QtGui.QFont("Times", 10, QtGui.QFont.Bold)
    self.label1.setFont(label1_font)

    self.table_widget = QtWidgets.QTableWidget(self)
    self.table_widget.setColumnCount(5)
    self.table_widget.setRowCount(3)

    self.font = QtGui.QFont()
    self.font.setFamily("Arial Black")
    self.font.setPointSize(10)
    
    self.table_widget.setHorizontalHeaderLabels(['Point','SiO2','Ce2O3','La2O3','ThO2'])
    self.table_widget.horizontalHeaderItem(0).setFont(self.font)
    self.table_widget.horizontalHeaderItem(1).setFont(self.font)
    self.table_widget.horizontalHeaderItem(2).setFont(self.font)
    self.table_widget.horizontalHeaderItem(3).setFont(self.font)
    self.table_widget.horizontalHeaderItem(4).setFont(self.font)
    self.table_widget.verticalHeader().hide()
    self.table_widget.setItem(0,0,QTableWidgetItem('1'))
    self.table_widget.setItem(0,1,QTableWidgetItem('54.5'))
    self.table_widget.setItem(0,2,QTableWidgetItem('0'))
    self.table_widget.setItem(0,3,QTableWidgetItem('18.5'))
    self.table_widget.setItem(0,4,QTableWidgetItem('27'))
    self.table_widget.setItem(1,0,QTableWidgetItem('2'))
    self.table_widget.setItem(1,1,QTableWidgetItem('65.0'))
    self.table_widget.setItem(1,2,QTableWidgetItem('12.5'))
    self.table_widget.setItem(1,3,QTableWidgetItem(''))
    self.table_widget.setItem(1,4,QTableWidgetItem('22.5'))
    self.table_widget.setItem(2,0,QTableWidgetItem('3'))
    self.table_widget.setItem(2,1,QTableWidgetItem('22.0'))
    self.table_widget.setItem(2,2,QTableWidgetItem('33.5'))
    self.table_widget.setItem(2,3,QTableWidgetItem('15.0'))
    self.table_widget.setItem(2,4,QTableWidgetItem('29.5'))
    


    self.button1 = QPushButton(self)
    self.button1.setText("Click to upload csv")
    self.button1.setFont(self.font)
    self.button1.clicked.connect(self.upload)

    self.button2 = QPushButton(self)
    self.button2.setText("Submit")
    self.button2.setFont(self.font)
    self.button2.clicked.connect(self.openWindow)

    self.prg_bar = QProgressBar(self)
    self.prg_bar.setStyle(QStyleFactory.create("Windows"))
    self.prg_bar.setTextVisible(True)
    self.prg_bar.setMaximum(100)

    layout1 = QVBoxLayout(self)
    layout1.addWidget(self.label1)
    layout1.addWidget(self.table_widget)
    layout1.addWidget(self.button1)
    layout1.addWidget(self.button2)
    layout1.addWidget(self.prg_bar)
    
    self.show()

  def upload(self):
    self.fname, _ = QFileDialog.getOpenFileName(self.button1,"Open File", "", "CSV files (*.csv)")

  
  def openWindow(self):
              
    try:
      if self.fname:
        user_df = pd.read_csv(self.fname)
        
        self.worker = WorkerThread(user_df)
        self.worker.start()
        self.worker.progress.connect(self.update_progress)
        self.worker.update.connect(self.display_output)
                      
    except:

      msg = QMessageBox()
      msg.setWindowIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MessageBoxWarning))
      msg.setWindowTitle("Warning")
      msg.setText("Please upload file and then click submit")
      msg.exec_()

  def display_output(self,result_df, ree_df):
    self.window2 = Window2(result_df,ree_df)
    self.window2.show()


  def update_progress(self, val):
    self.prg_bar.setValue(val)
   
 
if __name__ == '__main__':
  app = QApplication(sys.argv)
  window = Window1()
  sys.exit(app.exec_())
