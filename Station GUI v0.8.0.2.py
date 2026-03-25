import graficador_v12 as gf
import BaseDeDatos_Lib_v04 as bd
import pandas as pd
import os
import seaborn as sns


import wx
import wx.xrc

from matplotlib.figure import Figure

from matplotlib.backends.backend_wxagg import \
 \
    FigureCanvasWxAgg as FigCanvas, \
 \
    NavigationToolbar2WxAgg as NavigationToolbar

import numpy as np

from sqlalchemy import create_engine
from sqlalchemy.types import String

#dirDatos = os.path.normpath('//PC/AutomaticStation')
#dirDatos = os.path.normpath('/mnt/PC/AutomaticStation')
dirDatos = os.path.normpath('./')
#dirDatos = os.path.normpath('//Reactivos/o3/O3_SN_49C-58546-318')
#dirDatos2 = os.path.normpath('//Reactivos/o3/O3_SN_0330102717')

engine = create_engine('postgresql://postgres:vag@10.30.19.5:5432/GAWUSH_DATABASE')

from PIL import Image
def get_concat_h_multi_resize(im_list, resample=Image.BICUBIC):
    min_height = min(im.height for im in im_list)
    im_list_resize = [im.resize((int(im.width * min_height / im.height), min_height),resample=resample)
                      for im in im_list]
    total_width = sum(im.width for im in im_list_resize)
    dst = Image.new('RGB', (total_width, min_height))
    pos_x = 0
    for im in im_list_resize:
        dst.paste(im, (pos_x, 0))
        pos_x += im.width
    return dst

def get_concat_v_multi_resize(im_list, resample=Image.BICUBIC):
    min_width = min(im.width for im in im_list)
    im_list_resize = [im.resize((min_width, int(im.height * min_width / im.width)),resample=resample)
                      for im in im_list]
    total_height = sum(im.height for im in im_list_resize)
    dst = Image.new('RGB', (min_width, total_height))
    pos_y = 0
    for im in im_list_resize:
        dst.paste(im, (0, pos_y))
        pos_y += im.height
    return dst

def get_concat_tile_resize(im_list_2d, resample=Image.BICUBIC):
    im_list_v = [get_concat_h_multi_resize(im_list_h, resample=resample) for im_list_h in im_list_2d]
    return get_concat_v_multi_resize(im_list_v, resample=resample)


def crear(fig_temp, axes_Temp, filename):

    extent = axes_Temp.get_window_extent().transformed(fig_temp.dpi_scale_trans.inverted())

    fig_temp.savefig(filename, dpi=300, bbox_inches=extent.expanded(1.1, 1.2))

    im1 = Image.open(filename)
    im2 = Image.open('SMN_Logo.jpg')
    im3 = Image.open('TDF_Logo.jpg')
    get_concat_tile_resize([[im1],
                            [im2, im2, im2, im2, im2, im3]]).save(filename)

def crearGeneral(fig, axes, filename='General'):
    extent = fig.get_window_extent().transformed(fig.dpi_scale_trans.inverted())

    fig.savefig(filename, dpi=300, bbox_inches=extent.expanded(0.8, 0.85))

    im1 = Image.open(filename)
    im2 = Image.open('SMN_Logo.jpg')
    im3 = Image.open('TDF_Logo.jpg')
    get_concat_tile_resize([[im1],
                            [im2, im2, im2, im2, im2, im3]]).save(filename)

class ConfigBox(wx.Panel):
    """
    """

    def __init__(self, parent, ID, label, boton, actual, initval):
        wx.Panel.__init__(self, parent, ID)

        self.value = initval

        box = wx.StaticBox(self, -1, label, )

        config = wx.StaticBoxSizer(box, wx.VERTICAL)
        #sizer.Add(self.radio_auto, 0, wx.ALL, 10)

        self.configActual = wx.StaticText( config.GetStaticBox(), wx.ID_ANY, actual, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.configActual.Wrap( -1 )
        config.Add( self.configActual, 0, wx.ALL, 5 )

        self.InputConfig = wx.TextCtrl( config.GetStaticBox(), wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        config.Add( self.InputConfig, 0, wx.ALL, 5 )

        self.FijarConfig = wx.Button( config.GetStaticBox(), wx.ID_ANY, boton, wx.DefaultPosition, wx.DefaultSize, 0 )
        config.Add( self.FijarConfig, 0, wx.ALL, 5 )
        self.SetSizer(config)

        config.Fit(self)

class Button(wx.Panel):
    """
    """

    def __init__(self, parent, ID, boton,):
        wx.Panel.__init__(self, parent, ID)


        box = wx.StaticBox(self, -1,  )

        config = wx.StaticBoxSizer(box, wx.VERTICAL)


        self.AccionBoton = wx.Button( config.GetStaticBox(), wx.ID_ANY, boton, wx.DefaultPosition, wx.DefaultSize, 0 )
        config.Add( self.AccionBoton, 0, wx.ALL, 5 )
        self.SetSizer(config)

        config.Fit(self)

class MagMedidaUnidad(wx.Panel, ):
    def __init__(self, parent, Text1='label1', Text2='label2', Text3='label3'):
        wx.Panel.__init__(self, parent)
        bSizer21 = wx.BoxSizer(wx.HORIZONTAL)

        self.m_staticText4 = wx.StaticText(self, wx.ID_ANY, Text1, wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText4.Wrap(-1)
        bSizer21.Add(self.m_staticText4, 0, wx.ALL, 0)

        self.m_staticText5 = wx.StaticText(self, wx.ID_ANY, Text2, wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText5.Wrap(-1)
        bSizer21.Add(self.m_staticText5, 0, wx.ALL, 0)

        self.m_staticText6 = wx.StaticText(self, wx.ID_ANY, Text3, wx.DefaultPosition, wx.DefaultSize, 0)
        self.m_staticText6.Wrap(-1)
        bSizer21.Add(self.m_staticText6, 0, wx.ALL, 0)
        self.SetSizer(bSizer21)

class Status_AWS(wx.Panel):
    """
    """

    def __init__(self, parent, ID, Titulo, data,):
        wx.Panel.__init__(self, parent, ID)
        test = wx.BoxSizer(wx.HORIZONTAL)
        PrimeraColumna = wx.BoxSizer(wx.VERTICAL)
        SegundaColumna = wx.BoxSizer(wx.VERTICAL)

        dataNotNa = data.dropna(axis=1, how='all')
        self.FechaHora = MagMedidaUnidad(self, 'Fecha y Hora: ',dataNotNa.tail(1).index[0]._date_repr, '\n '+dataNotNa.tail(1).index[0]._time_repr[:8])
        self.Temperatura = MagMedidaUnidad(self, 'Temperatura: ',  f'{dataNotNa.ta_avg.tail(1)[0]:.1f}', ' °C')
        self.Presion = MagMedidaUnidad(self, 'Presion: ', f'{dataNotNa.pa_avg.tail(1)[0]:.1f}', ' hPa')
        self.Humedad = MagMedidaUnidad(self, 'Humedad: ', f'{dataNotNa.rh_avg.tail(1)[0]:.1f}', ' %')
        self.Rapidez = MagMedidaUnidad(self, 'Intensidad: ', f'{dataNotNa.ws_avg1.tail(1)[0]:.1f}', ' m/s')
        self.Direccion = MagMedidaUnidad(self, 'Direccion: ', f'{dataNotNa.wd_avg1.tail(1)[0]:.1f}', ' Grad')

        test.Add(self.FechaHora, 0, wx.ALL, 5)
        PrimeraColumna.Add(self.Temperatura, 0, wx.ALL, 5)
        PrimeraColumna.Add(self.Presion, 0, wx.ALL, 5)
        PrimeraColumna.Add(self.Humedad, 0, wx.ALL, 5)
        SegundaColumna.Add(self.Rapidez, 0, wx.ALL, 5)
        SegundaColumna.Add(self.Direccion, 0, wx.ALL, 5)
        test.Add(PrimeraColumna, 0, wx.ALL, 5)
        test.Add(SegundaColumna, 0, wx.ALL, 5)
        self.SetSizer(test)

        test.Fit(self)


class StatusBox(wx.Panel):
    """
    """

    def __init__(self, parent, ID, label, initval):
        wx.Panel.__init__(self, parent, ID)

        self.value = initval

        box = wx.StaticBox(self, -1, label, )

        config = wx.StaticBoxSizer(box, wx.VERTICAL)

        self.colour = wx.Colour(0, 0, 0)
        self.panelStatus = wx.Panel(config.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition, (50, 100), wx.TAB_TRAVERSAL)
        self.panelStatus.SetBackgroundColour(self.colour)

        config.Add(self.panelStatus, 0, wx.ALL, 5)
        self.SetSizer(config)

        config.Fit(self)



def buscarEnBaseDeDatos(inicio, fin, ext = '.csv' ):
    """
    try:
        df_siap = bd.buscarEnBaseDeDatos(engine, "SIAP", inicio, fin)
        df_siap.DateTime = pd.to_datetime(df_siap.DateTime)
        df_siap.set_index(['DateTime'], inplace=True)
        df_siap['DateTime'] = df_siap.index
        df_siap.rename({'TambC': 'TempA', 'Hr': 'HR', 'PrhPa': 'Pres', 'VdGrad': 'Dir'}, axis=1, inplace=True)
    except:
        #Ubic, TempA, HR, Pres, ViMS, Dir, RadWm2, PPmm, TsueC, DateTime
        print("No se pudo Obtener Datos de " + inicio._repr_base)
        df_siap = pd.DataFrame()
    """
    try:
        df_aw810 = bd.buscarEnBaseDeDatos(engine, "aws810", inicio, fin)
        df_aw810.DateTime = pd.to_datetime(df_aw810.DateTime)
        df_aw810.set_index(['DateTime'], inplace=True)
        df_aw810.dropna(axis='columns', how='all', inplace=True)
        df_aw810['DateTime'] = df_aw810.index
    except:
        print("No se pudo Obtener Datos de " + inicio._repr_base)
        df_aw810 = pd.DataFrame()
    #df_aux = pd.concat([df_siap, df_aw810], axis=1)
    return df_aw810

class VentanaPrincipal ( wx.Frame ):

    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"Ushuaia GAW Station Ozone", pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
        self.HoraInicio = pd.to_datetime('00:00')

        self.config()

        self.obtenerDatos()
        self.estructuraPrincipal()

        self.compartir.AccionBoton.Bind(wx.EVT_BUTTON, self.CrearImagen)

        self.redraw_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_redraw_timer, self.redraw_timer)
        self.redraw_timer.Start(30000)


        self.Bind(wx.EVT_CLOSE, self.closeWindow)  # Bind the EVT_CLOSE event to closeWindow()

    def config(self):
        pass



    def obtenerDatos(self):
        hoy = pd.to_datetime('today')
        ayer = hoy - pd.to_timedelta(1, unit='D')
        #df = pd.concat([ buscarDatos(hoy-pd.to_timedelta(1,unit='D')), buscarDatos(hoy)]) # Ayer y Hoy
        df = pd.DataFrame() #
        df = pd.concat([buscarEnBaseDeDatos(ayer.floor('D'), ayer.ceil('D')), buscarEnBaseDeDatos(hoy.floor('D'), hoy.ceil('D'))])  # Ayer y Hoy



        self.data = df

        """if df.empty: #Funcion que solo da Valores para completar.
            X = 1440
            Example = pd.DataFrame()
            Example['DateTime'] = pd.date_range(end=pd.Timestamp('today'), freq='T', periods=X)
            Y = list()
            c= (np.random.rand()-1)
            for x in (Example.DateTime - pd.to_datetime('2020-01-01')).dt.total_seconds():
                Y.append(100*np.sin(x / 15000)*c+30*np.cos(x / 10000)*np.random.rand())
            Example['TempA'] = Y
            Example['TempS'] = Y
            Example['HR'] = Y
            Example['ViMS'] = Y
            Example['Dir'] = np.rad2deg(np.deg2rad([(i*3) % 360 for i in Y]))
            Example['Dir'] = Example['Dir'] * (Example['Dir']>=0) + (Example['Dir'] +180) * (Example['Dir'] < 0)
            Example['RadWm2'] = Y
            Example['Pres'] = Y
            Example.set_index('DateTime', drop=False, inplace=True)
            self.data = Example"""




    def init_plot(self):
        sns.set()
        self.dpi = 100
        self.fig = Figure((3.0, 3.0), dpi=self.dpi)
        self.fig.suptitle('Estacion Automatica SIAP', size=12)
        #Temperatura
        self.axes_Temp = self.fig.add_subplot(231)
        self.plot_Temp = gf.axTemp(self.axes_Temp, self.data)
        #Humedad
        self.axes_Humd = self.fig.add_subplot(232)
        self.plot_Humd = gf.axHR(self.axes_Humd, self.data)
        #Presion
        self.axes_Pres = self.fig.add_subplot(234)
        self.plot_Pres = gf.axPres(self.axes_Pres, self.data)

        #Viento Rapidez
        self.axes_VRap = self.fig.add_subplot(233)
        self.plot_VRap = gf.axVRap(self.axes_VRap, self.data)

        #self.axes_VGra_TEST = self.axes_VRap.twinx()
        #self.plot_VGra = gf.axVGra(self.axes_VGra_TEST, self.data)

        # Viento Direccion
        self.axes_VGra = self.fig.add_subplot(236)
        self.plot_VGra = gf.axVGra(self.axes_VGra, self.data)

        #Radiacion
        self.axes_Rad = self.fig.add_subplot(235)
        self.plot_Rad = gf.axRad(self.axes_Rad, self.data)


    def on_redraw_timer(self, event):
        self.obtenerDatos()
        self.draw_plot()
        self.ActualizarStatus()


    def On_FijarDuracion(self, event):
        btn = event.GetEventObject().GetLabel()
        print(btn)
        #Cambiar Duracion
        String = self.duracion.InputConfig.GetValue()
        self.duracion.InputConfig.SetValue("")
        print(String)
        try:
            if int(String) <= 0:
                return
        except:
            print("ERROR fijando Duracion")
            return
        self.CalDuracion = String #

        #Actualizar *.ini
        configuracion = open('TECOconfig.ini', 'r')
        lineas = configuracion.readlines()
        configuracion.close()
        for i in range(0, len(lineas)):
            if lineas[i][:26] == 'Duracion Calibracion[min]:':
                lineas[i] = 'Duracion Calibracion[min]: ' + self.CalDuracion + '\n'
        print(lineas)
        configuracion = open('TECOconfig.ini', 'w')
        configuracion.write(''.join(lineas))
        configuracion.close()

    def On_FijarHora(self, event):
        btn = event.GetEventObject().GetLabel()
        print(btn)
        #Cambiar Hora de inicio
        String = self.hora.InputConfig.GetValue()
        self.hora.InputConfig.SetValue("")
        try:
            if pd.isnull(pd.to_datetime(String)):
                return
        except:
            print("ERROR Fijando HORA")
            return
        self.CalInicio = pd.to_datetime(String)._time_repr[:5] # Se puede chequear que solo sea hora y no contenga dias

        #Actualizar *.ini
        configuracion = open('TECOconfig.ini', 'r')
        lineas = configuracion.readlines()
        configuracion.close()
        for i in range(0, len(lineas)):
            if lineas[i][:17] == 'Hora Calibracion:':
                lineas[i] = 'Hora Calibracion: ' + self.CalInicio + '\n'
        print(lineas)
        configuracion = open('TECOconfig.ini', 'w')
        configuracion.write(''.join(lineas))
        configuracion.close()

    def CrearImagen(self, event):
        crearGeneral(self.fig, self.axes_Temp, 'CompartirGeneral.jpg')
        crear(self.fig, self.axes_Temp, 'CompartirTemperatura.jpg')
        print("CREADO")

        pass

    def ActualizarEjeX(self, axes):
        axes.set_xbound(lower=pd.to_datetime('today') - pd.to_timedelta(1, unit='D'), upper=pd.to_datetime('today'))

    def ActualizarEjeY(self, axes, DATA):
        DATA = DATA.loc[~DATA.isnull()]
        if not(DATA.empty):
            axes.set_ybound(lower= min(list(DATA))-0.5, upper=max(list(DATA))+3)
        else:
            axes.set_ybound(lower=0, upper=3)

    def ActualizarPlot(self, ax, data, columna):
        # 1. Filtrar valores válidos (sin NaN)
        mask = data[columna].notna() & data['DateTime'].notna()
        x = data.loc[mask, 'DateTime'].to_numpy()
        y = data.loc[mask, columna].to_numpy()

        # 2. Ordenar por eje X si hay desorden
        orden = np.argsort(x)
        x = x[orden]
        y = y[orden]

        # 3. Actualizar los datos de la línea
        ax.set_xdata(x)
        ax.set_ydata(y)


    def draw_plot(self):
        dataTmin = self.data.resample('30T', label='right').mean().copy()
        dataTmin['DateTime'] = dataTmin.index

        #dataTminWind = pd.concat([gf.calVientoDirProm(self.data[['Dir']]),
        #                          gf.calVientoDirProm(self.data[['wd_avg1']])], axis=1)
        dataTminWind = gf.calVientoDirProm(self.data[['wd_avg1']])

        dataTminWind['DateTime'] = dataTminWind.index
        
        
        #TEMPERATURA
        self.ActualizarEjeX(self.axes_Temp)
        self.ActualizarEjeY(self.axes_Temp, self.data.ta_inst)

        self.ActualizarPlot(self.plot_Temp[0][0], self.data, 'ta_inst')
        self.ActualizarPlot(self.plot_Temp[1][0], dataTmin, 'ta_inst')

        #self.ActualizarPlot(self.plot_Temp[0][0], self.data, 'TempA')
        # self.ActualizarPlot(self.plot_Temp[1][0], self.data, 'ta_inst')
        #self.ActualizarPlot(self.plot_Temp[2][0], dataTmin, 'TempA')
        # self.ActualizarPlot(self.plot_Temp[3][0], dataTmin, 'ta_inst')
        #self.ActualizarPlot(self.plot_Temp[4][0], self.data, 'TsueC')

        #HUMEDAD
        self.ActualizarEjeX(self.axes_Humd)

        self.ActualizarPlot(self.plot_Humd[0][0], self.data, 'rh_inst')
        self.ActualizarPlot(self.plot_Humd[1][0], dataTmin, 'rh_inst')

        #self.ActualizarPlot(self.plot_Humd[0][0], self.data, 'HR')
        #self.ActualizarPlot(self.plot_Humd[1][0], self.data, 'rh_inst')
        #self.ActualizarPlot(self.plot_Humd[2][0], dataTmin, 'HR')
        #self.ActualizarPlot(self.plot_Humd[3][0], dataTmin, 'rh_inst')


        # PRESION
        self.ActualizarEjeX(self.axes_Pres)
        self.ActualizarEjeY(self.axes_Pres, self.data.pa_inst)

        self.ActualizarPlot(self.plot_Pres[0][0], self.data, 'pa_inst')
        self.ActualizarPlot(self.plot_Pres[1][0], dataTmin, 'pa_inst')


        #self.ActualizarPlot(self.plot_Pres[0][0], self.data, 'Pres')
        #self.ActualizarPlot(self.plot_Pres[1][0], self.data, 'pa_inst')
        #self.ActualizarPlot(self.plot_Pres[2][0], dataTmin, 'Pres')
        #self.ActualizarPlot(self.plot_Pres[3][0], dataTmin, 'pa_inst')


        # VIENTO RAPIDEZ
        self.ActualizarEjeX(self.axes_VRap)
        self.ActualizarEjeY(self.axes_VRap, self.data.ws_avg1)

        self.ActualizarPlot(self.plot_VRap[0][0], self.data, 'ws_avg1')
        self.ActualizarPlot(self.plot_VRap[1][0], dataTmin, 'ws_avg1')


        #self.ActualizarPlot(self.plot_VRap[0][0], self.data, 'ViMS')
        #self.ActualizarPlot(self.plot_VRap[1][0], self.data, 'ws_avg1')
        #self.ActualizarPlot(self.plot_VRap[2][0], dataTmin, 'ViMS')
        #self.ActualizarPlot(self.plot_VRap[3][0], dataTmin, 'ws_avg1')


        # Viento Direccion


        self.ActualizarEjeX(self.axes_VGra)

        self.ActualizarPlot(self.plot_VGra[0][0], self.data, 'wd_avg1')
        self.ActualizarPlot(self.plot_VGra[1][0], dataTminWind, 'wd_avg1')


        #self.ActualizarPlot(self.plot_VGra[0][0], self.data, 'Dir')
        #self.ActualizarPlot(self.plot_VGra[1][0], self.data, 'wd_avg1')
        #self.ActualizarPlot(self.plot_VGra[2][0], dataTminWind, 'Dir')
        #self.ActualizarPlot(self.plot_VGra[3][0], dataTminWind, 'wd_avg1')



        # Radiacion
        self.ActualizarEjeX(self.axes_Rad)
        self.ActualizarEjeY(self.axes_Rad, self.data.solar_rad_inst)

        self.ActualizarPlot(self.plot_Rad[0][0], self.data, 'solar_rad_inst')
        self.ActualizarPlot(self.plot_Rad[1][0], dataTmin, 'solar_rad_inst')



        #self.ActualizarPlot(self.plot_Rad[0][0], self.data, 'RadWm2')
        #self.ActualizarPlot(self.plot_Rad[1][0], self.data, 'solar_rad_inst')
        #self.ActualizarPlot(self.plot_Rad[2][0], dataTmin, 'RadWm2')
        #self.ActualizarPlot(self.plot_Rad[3][0], dataTmin, 'solar_rad_inst')

        self.canvas.draw()

    def ActualizarStatus(self):
        #self.Status.FechaHora.
        #Fecha y Hora

        dataNotNa = self.data.dropna(axis=1)
        self.Status.FechaHora.m_staticText5.SetLabel(dataNotNa.tail(1).index[0]._date_repr)
        self.Status.FechaHora.m_staticText6.SetLabel(' '+dataNotNa.tail(1).index[0]._time_repr[:8])
        #Temperatura
        self.Status.Temperatura.m_staticText5.SetLabel( f'{dataNotNa.ta_avg.tail(1)[0]:.1f}')
        #Presion
        self.Status.Presion.m_staticText5.SetLabel( f'{dataNotNa.pa_avg.tail(1)[0]:.1f}')
        # Humedad
        self.Status.Humedad.m_staticText5.SetLabel(f'{dataNotNa.rh_avg.tail(1)[0]:.1f}')
        # Intensidad
        self.Status.Rapidez.m_staticText5.SetLabel(f'{dataNotNa.ws_avg1.tail(1)[0]:.1f}')
        # Direccion
        self.Status.Direccion.m_staticText5.SetLabel(f'{dataNotNa.wd_avg1.tail(1)[0]:.1f}')

    def estructuraPrincipal(self):
        self.panel = wx.Panel(self)
        self.init_plot()
        self.canvas = FigCanvas(self.panel, -1, self.fig)
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.Status = Status_AWS(self.panel, -1, "Titulo", self.data)
        self.vbox.Add(self.Status, 0, flag=wx.ALIGN_RIGHT | wx.TOP)
        self.vbox.Add(self.canvas, 1, flag=wx.LEFT | wx.TOP | wx.GROW)

        #self.hora = ConfigBox(self.panel, -1, "Hora de Calibracion", "Fijar Hora", self.HoraInicio._repr_base, 0)
        #self.duracion = ConfigBox(self.panel, -1, "Duracion [en minutos]", "Fijar Duracion ", self.CalDuracion, 0)
        #self.StatusCal = StatusBox(self.panel, -1, self.PuertoCalibrador, 0)

        #self.hbox2 = wx.BoxSizer(wx.HORIZONTAL)

        #self.hbox2.Add(self.hora, border=5, flag=wx.ALL)
        #self.hbox2.Add(self.duracion, border=5, flag=wx.ALL)
        #self.hbox2.Add(self.StatusCal, border=5, flag=wx.ALL)

        #self.vbox.Add(self.hbox2, 0, flag=wx.ALIGN_LEFT | wx.TOP)
        self.compartir = Button(self.panel, -1,  "Compartir")
        self.vbox.Add(self.compartir, 0, flag=wx.ALIGN_RIGHT | wx.TOP)
        self.panel.SetSizer(self.vbox)
        self.vbox.Fit(self)



    def closeWindow(self, event):
        #print("CHAU")
        #self.SerialCal.close()
        self.Destroy()  # This will close the app window.
        wx.GetApp().ExitMainLoop()

    def __del__( self ):

        pass

if __name__ == '__main__':
    app = wx.App(False)

    app.frame = VentanaPrincipal(None)

    app.frame.Show(True)

    app.MainLoop()
