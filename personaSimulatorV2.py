import sys
from pathlib import Path
import csv
import datetime
import platform

from PySide6.QtWidgets import QMainWindow, QApplication
from PySide6.QtUiTools import loadUiType
from PySide6.QtCore import QTimer, QDateTime

from personafun.ardconn import ArdSimulator
from personafun.figurediagram import MplCanvas
from personafun.dbconn.dbapi import apiClean, createTempCap


#### Resource Path
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', Path(__file__).resolve().parent)
    return str(Path.joinpath(base_path,relative_path))

#### ui connect
ui_form = resource_path("personaGuiV2.ui")
form_class = loadUiType(ui_form)[0]

#### Window class
class BaseWindow(QMainWindow, form_class):

    def __init__(self, *args, **kwargs):
        super(BaseWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.setWindowTitle('Persona Temp.Cap. Simulator')
        self.initUI()
        self.initCanvas()
        self.initStart()
        self.pushBtn_run.setEnabled(True)
        self.system_cnt = 0

    #### initial UI contents : Logo
    def initUI(self):
        # Top Logo
        self.labelTopLogo.setStyleSheet('border-image:url(./img/python_logo.svg);border:0px;')
        # Sub Logo
        self.labelpersonaLogo.setStyleSheet('border-image:url(./img/logo_persona_450_150.png);border:0px;')
        
    def initCanvas(self):
        self.canvas1 = MplCanvas()
        self.graph1_verticalLayout.addWidget(self.canvas1)
        self.canvas2 = MplCanvas()
        self.graph2_verticalLayout.addWidget(self.canvas2)
        self.canvas3 = MplCanvas()
        self.graph3_verticalLayout.addWidget(self.canvas3)
        self.canvas4 = MplCanvas()
        self.graph4_verticalLayout.addWidget(self.canvas4)
    
    def initStart(self):
        self.text_display("Start Loop")
        dateTimeVar = QDateTime.currentDateTime()
        self.text_display(dateTimeVar.toString("yyyy-MM-dd | hh:mm:ss"))
        self.text_display("Platform Check : {}".format(platform_check[0:5]))
        
        self.timer = QTimer()
        self.timer.setInterval(sample_time)
        self.timer.timeout.connect(self.start_loop)
        self.timer.start()

        ## Button connect
        self.pushBtn_run.clicked.connect(self.run_btn)
        self.pushBtn_stop.clicked.connect(self.stop_btn)
        self.pushBtn_quit.clicked.connect(self.close)
    
    ########== Button Fun ==###############################################    
    def run_btn(self):
        global data_sum, finish_cnt
        self.system_cnt = 0
        data_sum = []
        finish_cnt = 1*60*60
        self.text_display("Daq Run....")
        apiClean()
        self.text_display("Table:TempCap Complete Api Clean")
        self.pushBtn_run.setDisabled(True)
        
        self.lcdID.display(self.system_cnt)
        self.lcdID.setDigitCount(4)
        self.lcdSaveCount.display(save_cnt)
        self.lcdSaveCount.setDigitCount(5)
        self.lcdFinishCount.display(finish_cnt)
        self.lcdFinishCount.setDigitCount(5)
        
        self.timer = QTimer()
        self.timer.setInterval(sample_time)
        self.timer.timeout.connect(self.daq_loop)
        self.timer.start()
        
    def stop_btn(self):
        self.text_display("Daq Stop... Timer stop")
        self.timer.stop()
        
    ########== UI Display ==###############################################    
    def text_display(self,to_text):
        self.textBrowser.append(to_text)
    
    def lcd_display_update(self, loop_cnt, data):
        dateTimeVar = QDateTime.currentDateTime()
        self.lcdID.display(loop_cnt)
        self.lcdID.setDigitCount(4)
        self.lcdTime.display(dateTimeVar.toString("yy-MM-dd,hh:mm:ss"))
        self.lcdTime.setDigitCount(17)
        self.lcdTemp.display(data[4])
        self.lcdTemp.setDigitCount(5)
        self.lcdSystemSampleTime.display(data[3])
        self.lcdSystemSampleTime.setDigitCount(5)
        self.lcdCapacity.display(data[6])
        self.lcdCapacity.setSmallDecimalPoint(True)
        self.lcdCapacity.setDigitCount(5)
        self.lcdADC.display(data[5])
        self.lcdADC.setSmallDecimalPoint(True)
        self.lcdADC.setDigitCount(5)
        
            
    def plot_show(self,data_sum):
        global save_cnt, loop_cnt
        x = []
        y1 = []
        y2 = []
        y3 = []
        y4 = []
        ADC_max = 1023
        for data in data_sum:
            x.append(int(data[0]))
            y1.append(round(float(data[4]),1))
            y2.append(int(data[5]))
            y3.append(round(float(data[6]),1))
            y4.append(round(float(int(data[5])*5/ADC_max),1))
        ys = [y1,y2,y3,y4]
        canvas_list = [self.canvas1,self.canvas2,self.canvas3,self.canvas4]
        canvas_markers = ['ro-','go-','bo-','mo-']
        canvas_labels = ['Temp.','ADC','Cap.','Volt']
        for i in range(len(canvas_list)):
            canvas_list[i].axes.cla()
            canvas_list[i].axes.set_facecolor("black")
            canvas_list[i].axes.plot(x,ys[i],canvas_markers[i],label=canvas_labels[i])
            canvas_list[i].axes.xaxis.set_tick_params(color='white',labelcolor='white')
            canvas_list[i].axes.yaxis.set_tick_params(color='white',labelcolor='white',)
            canvas_list[i].axes.set_title(canvas_labels[i],color='white')
            canvas_list[i].axes.set_xlabel('Time',color='white')
            canvas_list[i].axes.set_ylabel(canvas_labels[i],color='white')
            canvas_list[i].axes.legend(loc="lower right")
            canvas_list[i].axes.grid()
            canvas_list[i].draw()
        
    ## start loop
    def start_loop(self):
        global data_sum
        test_loop = 100
        self.system_cnt += 1
        datetime_now = QDateTime.currentDateTime()
        date_now = datetime_now.toString("yyMMdd")
        time_now = datetime_now.toString("hhmmss")
        
        datetime_list = [self.system_cnt, date_now, time_now]
        ### Dev. Simulation Mode Open
        get_sim_data = ArdSimulator(sample_time).get_data()
        data_now = datetime_list + get_sim_data
        print(data_now)
        self.lcd_display_update(self.system_cnt, data_now)
        
        data_sum.append(data_now)
        self.plot_show(data_sum)
        
        if self.system_cnt % test_loop == 0:
            data_sum = []
            self.system_cnt = 0
    
    ## run loop after push Run
    def daq_loop(self):
        global data_sum, save_cnt, finish_cnt
        self.system_cnt += 1
        datetime_now = QDateTime.currentDateTime()
        date_now = datetime_now.toString("yyMMdd")
        time_now = datetime_now.toString("hhmmss")
        
        datetime_list = [self.system_cnt, date_now, time_now]
        ### Dev. Simulation Mode Open
        get_sim_data = ArdSimulator(sample_time).get_data()
        data_now = datetime_list + get_sim_data
        self.lcd_display_update(self.system_cnt, data_now)
        
        data_sum.append(data_now)
        self.plot_show(data_sum)
        
        if self.system_cnt % save_cnt == 0:
            self.timer.stop()
            self.close()
        elif self.system_cnt == finish_cnt:
            self.timer.stop()
            self.close()
        else:
            ### data-save
            with open(save_path, 'a') as fb:
                wr = csv.writer(fb)
                wr.writerow(data_now)
            ### to data-base
            dataset = data_now[1:]
            createTempCap(dataset)


#### Start Code ####
## initial variable
sample_time = 1000
save_cnt = 500
data_sum = []

## check form
platform_check = platform.platform()

## define: data header
# data_header = ['id','date','time','sampletime','temp','adc','capacitance']

## define: save path
#### save base path set
base_path = Path(__file__).resolve().parent
save_dir_name = 'savedata'
save_base = base_path.joinpath(save_dir_name)
#### save path from time: year-month-day_hour:minute:second
datetime_now = datetime.datetime.now()
save_sub_name_from_time = datetime_now.strftime("%y%m%d_%H%M%S")

save_path = save_base.joinpath(save_sub_name_from_time)
if save_base.is_dir() == False:
    save_base.mkdir()

#### End Code ####


if __name__=="__main__":
    app = QApplication(sys.argv)
    window = BaseWindow()
    window.show()
    app.exec()