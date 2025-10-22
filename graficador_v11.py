#import serial
import pandas as pd

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import os
import matplotlib.dates as mdates
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()

#dirDatos = os.path.normpath('//mnt/PC/AutomaticStation')
dirDatos = os.path.normpath('./')




def CalAngulo(arcC, arcS):
    if (arcC >= 0) & (arcS >= 0):  # Primer Cuadrante
        return arcC #, arcS
    if (arcC < 0) & (arcS >= 0):  # Segundo Cuadrante
        return arcC #, arcS
    if (arcC < 0) & (arcS < 0):  # Tercer Cuadrante
        return 2 * np.pi - arcC #, arcS
    if (arcC >= 0) & (arcS < 0):  # Cuarto Cuadrante
        return 2 * np.pi - arcC #, arcS
    return -999


def CalVientoComp(datos):
    datos['ViX'] = datos.ViMS * np.cos(datos.Dir) #
    datos['ViY'] = datos.ViMS * np.sin(datos.Dir) #
    datos['MOD'] = (datos.ViX ** 2.0 + datos.ViY ** 2.0) ** 0.5

    datos['ANG_C'] = np.arccos(datos.ViX/datos.MOD)
    datos['ANG_S'] = np.arcsin(datos.ViY/datos.MOD)
    #datos['ANG'] = np.nan
    datos['ANG'] = datos.apply(lambda x: CalAngulo(x['ANG_C'], x['ANG_S']), axis=1)
    datosProm = pd.DataFrame( columns=['ViX','ViY','ViXSTD','ViYSTD'])

    for hora in pd.date_range(datos.head(1).index[0]._date_repr, datos.tail(1).index[0],
                             freq='H', closed='left'):
        ViX = datos.ViX.loc[(datos.index >= pd.Timestamp(hora)) & (datos.index < pd.Timestamp(hora) + pd.Timedelta(hours=1))]
        ViY = datos.ViY.loc[(datos.index >= pd.Timestamp(hora)) & (datos.index < pd.Timestamp(hora) + pd.Timedelta(hours=1))]
        datosProm.loc[hora] = [ViX.mean(), ViY.mean(), ViX.std(), ViY.std()]
        #print(hora)
    datosProm['MOD'] = (datosProm.ViX ** 2.0 + datosProm.ViY ** 2.0) ** 0.5
    datosProm['ANG_C'] = np.arccos(datosProm.ViX / datosProm.MOD)
    datosProm['ANG_S'] = np.arcsin(datosProm.ViY / datosProm.MOD)
    datosProm['ANG'] = datosProm.apply(lambda x: CalAngulo(x['ANG_C'], x['ANG_S']), axis=1)

    return datos, datosProm

def grafViento(datos, ax):

    ax = ax or plt.gca()
    #sns.set()
    datos, promH = CalVientoComp(datos)
    #fig, ax = plt.subplots()
    ax = plt.subplot(111, projection='polar')
    ax.set_theta_direction(-1)
    ax.set_theta_offset(np.pi/2)

    ax.scatter(datos.Dir, datos.ViMS, s=4)
    ax.scatter(datos.ANG, datos.MOD, s=1)

    transp = np.linspace(0.1, 1, len(promH), endpoint=False)
    ax.bar(promH.ANG, promH.MOD, width=0.1, bottom=0.0, alpha=0.99)
    return  ax

def grafHR(datos):
    fig, ax = plt.subplots()

    ax.plot(datos.index, datos.HR, marker='o')
    HR_patch = mpatches.Patch(color='blue', label='Humedad')
    plt.legend(handles=[HR_patch])
    plt.ylim(0, 100)
    limHoraFinal = pd.Timestamp('today').round('min')
    limHoraInicial = limHoraFinal - pd.to_timedelta(3,unit='H')
    plt.xlim(limHoraInicial, limHoraFinal)
    plt.grid(True)
    # plt.axes.Axes.set_xlabel('time [s]')
    # plt.set_ylabel('Damped oscillation [V]')
    fig.subplots_adjust(right=0.98, top=0.98)
    ax.set_xlabel('Hora')
    ax.set_ylabel('Presion')
    #plt.show()
    return fig, ax




def grafPres(datos):
    fig, ax = plt.subplots()

    ax.plot(datos.index, datos.Pres)
    Pres_patch = mpatches.Patch(color='blue', label='Presion')
    plt.legend(handles=[Pres_patch])
    plt.ylim(0, 1100)
    limHoraFinal = pd.Timestamp('today').round('min')
    limHoraInicial = limHoraFinal - pd.to_timedelta(3,unit='H')
    plt.xlim(limHoraInicial, limHoraFinal)
    plt.ylim(min(datos.Pres) - 2, max(datos.Pres) + 2)
    plt.grid(True)
    # plt.axes.Axes.set_xlabel('time [s]')
    # plt.set_ylabel('Damped oscillation [V]')
    ax.set_xlabel('Hora')
    ax.set_ylabel('Presion')
    #plt.show()
    return fig, ax



def grafTemp(datos):
    #ax = ax or plt.gca()
    fig, ax = plt.subplots()

    ax.plot(datos.index, datos.TempA)
    tempA_patch = mpatches.Patch(color='blue', label='Temp Aire')
    plt.legend(handles=[tempA_patch])
    ax.plot(datos.index, datos.TempS)
    tempS_patch = mpatches.Patch(color='red', label='Temp Suelo')
    plt.legend(handles=[tempA_patch, tempS_patch])

    plt.ylim(np.around(min(datos.TempS.min(), datos.TempA.min()) - 2), np.around(max(datos.TempS.max(), datos.TempA.max()) + 2))
    limHoraFinal = pd.Timestamp('today').round('min')
    limHoraInicial = limHoraFinal - pd.to_timedelta(3,unit='H')
    plt.xlim(limHoraInicial, limHoraFinal)
    plt.grid(True)
    # plt.axes.Axes.set_xlabel('time [s]')
    # plt.set_ylabel('Damped oscillation [V]')
    ax.set_xlabel('Hora')
    ax.set_ylabel('Temperatura C')

    return
    #plt.show()

def grafTempSNS(datos):
    sns.set()
    #datos['DateTime'] = pd.to_datetime(datos.DATE + ' ' + datos.TIME)
    #datos.set_index('DateTime', inplace=True)
    #datos['O3'] = datos.apply(lambda x: O3_999toNan(x['O3']), axis=1)
    fig, ax = plt.subplots()

    ax.plot(datos.index, datos.TempA)
    tempA_patch = mpatches.Patch(color='blue', label='Temp Aire')
    plt.legend(handles=[tempA_patch])
    ax.plot(datos.index, datos.TempS)
    tempS_patch = mpatches.Patch(color='red', label='Temp Suelo')
    plt.legend(handles=[tempA_patch, tempS_patch])

    plt.ylim(np.around(min(datos.TempS.min(), datos.TempA.min()) - 2), np.around(max(datos.TempS.max(), datos.TempA.max()) + 2))
    limHoraFinal = pd.Timestamp('today').round('min')
    limHoraInicial = limHoraFinal - pd.to_timedelta(3,unit='H')
    plt.xlim(limHoraInicial, limHoraFinal)
    plt.grid(True)
    # plt.axes.Axes.set_xlabel('time [s]')
    # plt.set_ylabel('Damped oscillation [V]')
    ax.set_xlabel('Hora')
    ax.set_ylabel('Temperatura C')
    #plt.show()
    return fig, ax

def axHR(ax, data):
    data10min = data.resample('30T', label='right').mean()
    data10min['DateTime'] = data10min.index
    plot_data_00 = ax.plot(data.DateTime, data.HR, alpha=1, color='tab:blue')
    plot_data_01 = ax.plot(data.DateTime, data.rh_inst, alpha=.5, color='tab:orange')
    plot_data_02 = ax.plot(data10min.DateTime, data10min.HR, alpha=1, color='blue', linewidth=2)
    plot_data_03 = ax.plot(data10min.DateTime, data10min.rh_inst, alpha=1, color='orange', linewidth=2)
    HR_patch = mpatches.Patch(color='blue', label='Humedad Siap')
    HR_patch_2 = mpatches.Patch(color='orange', label='Humedad aws810')
    ax.legend(handles=[HR_patch, HR_patch_2])
    ax.axes.set_ylim(0, 100)
    limHoraFinal = pd.Timestamp('today').round('min')
    limHoraInicial = limHoraFinal - pd.to_timedelta(3,unit='H')
    ax.axes.set_xlim(limHoraInicial, limHoraFinal)
    plt.grid(True)

    date_form = mdates.DateFormatter("%H:%M")
    ax.xaxis.set_major_formatter(date_form)

    ax.tick_params(direction='in', labelsize=6, length=20)
    ax.tick_params('x', labelrotation=45)
    #plt.show()
    return [plot_data_00, plot_data_01, plot_data_02, plot_data_03]

def axPPmm(ax):
    #fig, ax = plt.subplots()

    #ax.plot(datos.index, datos.Pres)
    Pres_patch = mpatches.Patch(color='blue', label='Precipitaciones')
    ax.legend(handles=[Pres_patch])
    ax.axes.set_ylim(0, ax.axes.viewLim.ymax)
    limHoraFinal = pd.Timestamp('today').round('min')
    limHoraInicial = limHoraFinal - pd.to_timedelta(3,unit='minute')
    ax.axes.set_xlim(limHoraInicial, limHoraFinal)

    plt.grid(True)
    # plt.axes.Axes.set_xlabel('time [s]')
    # plt.set_ylabel('Damped oscillation [V]')
    #ax.set_xlabel('Hora')
    #ax.set_ylabel('mm')
    ax.tick_params(direction='in', labelsize=6, length=20)
    ax.tick_params('x', labelrotation=45)
    #plt.show()
    return ax

def axVRap(ax, data):
    data10min = data.resample('30T', label='right').mean()
    data10min['DateTime'] = data10min.index

    plot_data_00 = ax.plot(data.DateTime, data.ViMS, alpha=1, color='tab:blue')
    plot_data_01 = ax.plot(data.DateTime, data.ws_inst_spd, marker='.', alpha=.5, color='tab:orange', markersize=1)
    plot_data_02 = ax.plot(data10min.DateTime, data10min.ViMS, alpha=1, color='blue', linewidth=2)
    plot_data_03 = ax.plot(data10min.DateTime, data10min.ws_inst_spd, alpha=1, color='orange', linewidth=2)
    Rap_patch = mpatches.Patch(color='blue', label='Intensidad Siap')
    Rap_patch_2 = mpatches.Patch(color='orange', label='Intensidad aws810')
    ax.legend(handles=[Rap_patch, Rap_patch_2])

    ax.axes.set_ylim(0, ax.axes.viewLim.ymax + 10)
    limHoraFinal = pd.Timestamp('today').round('min')
    limHoraInicial = limHoraFinal - pd.to_timedelta(24,unit='H')
    ax.axes.set_xlim(limHoraInicial, limHoraFinal)

    plt.grid(True)
    date_form = mdates.DateFormatter("%H:%M")
    ax.xaxis.set_major_formatter(date_form)
    ax.tick_params(direction='in', labelsize=6, length=20)
    ax.tick_params('x', labelrotation=45)
    return [plot_data_00, plot_data_01, plot_data_02, plot_data_03]

def calVientoDirProm(data):
    data = data.copy()
    data['sinDir'] = np.sin(np.deg2rad(data[data.columns[0]]))
    data['cosDir'] = np.cos(np.deg2rad(data[data.columns[0]]))
    data10min = data.resample('30T', label='right').mean()
    data10min[data.columns[0]] = (data10min.cosDir >= 0) * np.arctan(data10min.sinDir / data10min.cosDir) + \
                    (data10min.cosDir < 0) * (np.arctan(data10min.sinDir / data10min.cosDir) + np.pi)
    data10min[data.columns[0]] = np.rad2deg(data10min[data.columns[0]])
    data10min[data.columns[0]] = (360 + data10min[data.columns[0]]) * (data10min[data.columns[0]] < 0) + (data10min[data.columns[0]]) * (data10min[data.columns[0]] >= 0)

    return data10min[[data.columns[0]]]

def axVGra(ax, data):
    data10min = pd.concat([calVientoDirProm(data[['Dir']]), calVientoDirProm(data[['wd_inst_dir']])], axis=1)

    data10min['DateTime'] = data10min.index
    #data['sinDir'] = np.sin(np.deg2rad(data.Dir))
    #data['cosDir'] = np.cos(np.deg2rad(data.Dir))
    #data10min = data.resample('30T', label='right').mean()
    #data10min['DateTime'] = data10min.index
    #data10min.Dir = (data10min.cosDir >= 0) * np.arctan(data10min.sinDir / data10min.cosDir) + \
    #                (data10min.cosDir<0)*(np.arctan(data10min.sinDir/data10min.cosDir) + np.pi)
    #data10min.Dir = np.rad2deg(data10min.Dir)
    #data10min.Dir = (360 + data10min.Dir) * (data10min.Dir < 0) + (data10min.Dir) * (data10min.Dir >= 0)



    plot_data_00 = ax.plot(data.DateTime, data.Dir, alpha=.3, marker='.', color='tab:blue', linestyle='')
    plot_data_01 = ax.plot(data.DateTime, data.wd_inst_dir, alpha=.1, marker='.', color='tab:orange', linestyle='')
    plot_data_02 = ax.plot(data10min.DateTime, data10min.Dir, alpha=1, marker='.', color='blue', linewidth=.75)
    plot_data_03 = ax.plot(data10min.DateTime, data10min.wd_inst_dir, alpha=1, marker='.', color='orange', linewidth=.75)

    Dir_patch = mpatches.Patch(color='blue', label='Direccion Siap')
    Dir_patch_2 = mpatches.Patch(color='orange', label='Direccion aws810')
    ax.legend(handles=[Dir_patch, Dir_patch_2])

    #ax.axes.set_ylim(ax.axes.viewLim.ymin - 10, ax.axes.viewLim.ymax + 10)
    ax.axes.set_ylim(0, 360)
    limHoraFinal = pd.Timestamp('today').round('min')
    limHoraInicial = limHoraFinal - pd.to_timedelta(24,unit='H')
    ax.axes.set_xlim(limHoraInicial, limHoraFinal)

    plt.grid(True)
    date_form = mdates.DateFormatter("%H:%M")
    ax.xaxis.set_major_formatter(date_form)
    ax.yaxis.set_ticks(np.arange(0, 390, 30))
    ax.tick_params(direction='in', labelsize=6, length=20)
    ax.tick_params('x', labelrotation=45)
    return [plot_data_00, plot_data_01, plot_data_02, plot_data_03]

def axRad(ax, data):

    data10min = data.resample('30T', label='right').mean()
    data10min['DateTime'] = data10min.index
    plot_data_00 = ax.plot(data.DateTime, data.RadWm2, alpha=1)
    plot_data_01 = ax.plot(data.DateTime, data.solar_rad_inst, alpha=1, color='tab:orange')
    plot_data_02 = ax.plot(data10min.DateTime, data10min.RadWm2, alpha=1, color='blue', linewidth=3)
    plot_data_03 = ax.plot(data10min.DateTime, data10min.solar_rad_inst, alpha=1, color='orange', linewidth=3)

    Rad_patch = mpatches.Patch(color='blue', label='Radiacion Wm2')
    Rad_patch_2 = mpatches.Patch(color='orange', label='Radiacion Wm2')
    ax.legend(handles=[Rad_patch, Rad_patch_2])
    ax.axes.set_ylim(ax.axes.viewLim.ymin - 10, ax.axes.viewLim.ymax + 10)
    limHoraFinal = pd.Timestamp('today').round('min')

    limHoraInicial = pd.Timestamp('today').floor('D') + pd.to_timedelta(4.5, unit='H')
    if limHoraInicial > pd.Timestamp('today'):
        limHoraInicial = pd.Timestamp('today').floor('D')

    ax.axes.set_xlim(limHoraInicial, limHoraFinal)

    plt.grid(True)
    date_form = mdates.DateFormatter("%H:%M")
    ax.xaxis.set_major_formatter(date_form)
    ax.tick_params(direction='in', labelsize=6, length=20)
    ax.tick_params('x', labelrotation=45)
    return [plot_data_00, plot_data_01, plot_data_02, plot_data_03]

def axPres(ax, data):
    data10min = data.resample('30T', label='right').mean()
    data10min['DateTime'] = data10min.index
    plot_data_00 = ax.plot(data.DateTime, data.Pres, alpha=1, color='tab:blue')
    plot_data_01 = ax.plot(data.DateTime, data.pa_inst, alpha=1, color='tab:orange')
    plot_data_02 = ax.plot(data10min.DateTime, data10min.Pres, alpha=1, color='blue', linewidth=2)
    plot_data_03 = ax.plot(data10min.DateTime, data10min.pa_inst, alpha=1, color='orange', linewidth=2)

    Pres_patch = mpatches.Patch(color='blue', label='Presion Siap')
    Pres_patch_2 = mpatches.Patch(color='orange', label='Presion aws810')
    ax.legend(handles=[Pres_patch, Pres_patch_2])
    ax.axes.set_ylim(ax.axes.viewLim.ymin - 10, ax.axes.viewLim.ymax + 10)
    limHoraFinal = pd.Timestamp('today').round('min')
    limHoraInicial = limHoraFinal - pd.to_timedelta(12,unit='H')
    ax.axes.set_xlim(limHoraInicial, limHoraFinal)

    plt.grid(True)
    date_form = mdates.DateFormatter("%H:%M")
    ax.xaxis.set_major_formatter(date_form)
    ax.tick_params(direction='in', labelsize=6, length=20)
    ax.tick_params('x', labelrotation=45)
    return [plot_data_00, plot_data_01, plot_data_02, plot_data_03]

def axTemp(ax, data):

    data10min = data.resample('30T', label='right').mean()
    data10min['DateTime'] = data10min.index
    plot_data_00 = ax.plot(data.DateTime, data.TempA, alpha=0.6, linewidth=2, color='tab:blue')
    plot_data_04 = ax.plot(data.DateTime, data.TsueC, alpha=0.6, linewidth=2, color='tab:green')
    plot_data_01 = ax.plot(data.DateTime, data.ta_inst, alpha=0.6, linewidth=2, color='tab:orange')
    plot_data_02 = ax.plot(data10min.DateTime, data10min.TempA, alpha=1, color='blue', linewidth=2)
    plot_data_03 = ax.plot(data10min.DateTime, data10min.ta_inst, alpha=1, color='orange', linewidth=2)
    tempA_patch = mpatches.Patch(color='blue', label='Temp Aire Siap')
    tempA_patch_2 = mpatches.Patch(color='orange', label='Temp Aire aws810')
    tempA_patch_3 = mpatches.Patch(color='green', label='Temp Suelo Siap')
    ax.legend(handles=[tempA_patch, tempA_patch_2, tempA_patch_3])
    #tempS_patch = mpatches.Patch(color='red', label='Temp Suelo')
    #ax.legend(handles=[tempA_patch])#[tempA_patch, tempS_patch])

    limHoraFinal = pd.Timestamp('today').round('min')
    limHoraInicial = limHoraFinal - pd.to_timedelta(1,unit='H')
    ax.axes.set_xlim(limHoraInicial, limHoraFinal)
    date_form = mdates.DateFormatter("%H:%M")
    ax.xaxis.set_major_formatter(date_form)
    ax.tick_params(direction='in', labelsize=6, length=20)
    ax.tick_params('x', labelrotation=45)
    return [plot_data_00, plot_data_01, plot_data_02,plot_data_03, plot_data_04]

def axViento(ax):

    ax.set_theta_direction(-1)
    ax.set_theta_offset(np.pi/2)
    ax.set_xticklabels([])
    return  ax

def conjuntoGraf():
    datos = DataFrameFromFile()
    sns.set()
    x = [1, 2, 3]
    y = [1, 2, 3]
    a = [2, 3, 4]
    b = [5, 7, 5]

    fig = plt.figure()
    ax1 = plt.subplot2grid((2, 3), (0, 0),  projection='polar')
    ax2 = plt.subplot2grid((2, 3), (0, 1), colspan=2)
    ax3 = plt.subplot2grid((2, 3), (1, 0))
    ax4 = plt.subplot2grid((2, 3), (1, 1))
    ax5 = plt.subplot2grid((2, 3), (1, 2))

    datos, promH = CalVientoComp(datos)
    i=len(promH)
    for hora in pd.date_range(promH.head(1).index[0]._date_repr, promH.tail(1).index[0],
                              freq='H').sort_values(ascending=False)[:3]:
        #print (hora)
        ax1.bar(promH.ANG.loc[promH.index == hora], promH.MOD.loc[promH.index == hora], width=0.1, bottom=0.0, alpha=(i/len(promH))**2)
        i=i-1
    #ax1.bar(promH.ANG, promH.MOD, width=0.1, bottom=0.0, alpha=0.99)

    ax1.scatter(datos.ANG.loc[(datos.index >= promH.tail(1).index[0])],
                datos.MOD.loc[(datos.index >= promH.tail(1).index[0])], color='blue', s=1 )
    #print(datos.MOD.loc[(datos.index >= pd.Timestamp('today').round('h'))])
    axViento(ax1)

    ax2.plot(datos.index, datos.TempA)
    axTemp(ax2)
    ax3.plot(datos.index, datos.PPmm)
    axPPmm(ax3)
    ax4.plot(datos.index, datos.Pres)
    axPres(ax4)
    ax5.plot(datos.index, datos.HR)
    axHR(ax5)
    #ax2.scatter(a, b)
    #plt.show()
    return fig

def VientoSectores(Vrad):
    if (Vrad > 337.5) | (Vrad <= 22.5):
        return 'N'
    if (Vrad > 22.5) & (Vrad <= 67.5):
        return 'NE'
    if (Vrad > 67.5) & (Vrad <= 112.5):
        return 'E'
    if (Vrad > 112.5) & (Vrad <= 157.5):
        return 'SE'
    if (Vrad > 157.5) & (Vrad <= 202.5):
        return 'S'
    if (Vrad > 202.5) & (Vrad <= 247.5):
        return 'SW'
    if (Vrad > 247.5) & (Vrad <= 292.5):
        return 'W'
    if (Vrad > 292.5) & (Vrad <= 337.5):
        return 'NW'
    return "XXX"


def obtenerMarcas(datos):
    velMax = datos.ViMS.loc[datos.ViMS == datos.ViMS.max()]
    velMaxGrad = datos.Dir.loc[datos.ViMS == datos.ViMS.max()]
    tempAireMax = datos.TempA.loc[datos.TempA == datos.TempA.max()]
    tempAireMin = datos.TempA.loc[datos.TempA == datos.TempA.min()]
    #print(datos.tail(1))
    #print(velMax, tempAireMax, tempAireMin)
    #--- m/s (--- km/h), del --- (---°) a las --:--
    if len(velMax) != 0:
        velMaxSTR = (str(velMax[0]) + "m/s " + str(np.around(velMaxGrad[0] * 360 / np.pi / 2,2)) + '° [' +
                     str(np.around(velMax[0]*3.6,2)) + "km/h del " +
                     VientoSectores(np.around(velMaxGrad[0] * 360 / np.pi / 2,2)) + "] a las " +
                     velMax.index[0]._time_repr[:8] + " UTC")
    else:
        velMaxSTR = "---m/s ---° [---km/h del ---] a las --:--"

    #--.-°C a las --:--
    if len(tempAireMax) != 0:
        tempAireMaxSTR = (str(tempAireMax[0]) + "°C a las " + tempAireMax.index[0]._time_repr[:8] + " UTC")
    else:
        tempAireMaxSTR = "--.-°C a las --:--"

    #--.-°C a las --:--
    if len(tempAireMin) != 0:
        tempAireMinSTR = (str(tempAireMin[0]) + "°C a las " + tempAireMin.index[0]._time_repr[:8] + " UTC")
    else:
        tempAireMinSTR = "--.-°C a las --:--"

    return velMaxSTR, tempAireMaxSTR, tempAireMinSTR


def obtenerUltimoDato(datos):
    UltimoDato = datos.tail(1).copy()
    HoraD = "Datos de la hora --:--"
    TempA = "Temperatura del Aire: --.-°C"
    TempS = "Temperatura del Suelo: --.-°C"
    Press = "Presion: ----.- hPa"
    VeloV = "Velocidad del Viento: --- m / s(--- km / h), del --- (---°)"
    HuRel = "Humedad Relativa: ---.- %"
    Preci = "Precipitacion Acumulada: ---.- mm"
    Radia = "Radiacion: --.- W / m ^ 2"

    if len(UltimoDato) == 0:
        return
    HoraD = HoraD[:17] + UltimoDato.index[0]._time_repr[:5]

    #Temp AIRE
    if UltimoDato.TempA[0] != np.nan:
        TempA = TempA[:22] + str(UltimoDato.TempA[0]) + "°C"
    # Temp SUELO
    if UltimoDato.TempS[0] != np.nan:
        TempS = TempS[:23] + str(np.around(UltimoDato.TempS[0],2)) + "°C"
    #PRESION
    if UltimoDato.Pres[0] != np.nan:
        Press = Press[:9] + str(UltimoDato.Pres[0]) + "hPa"
    #HUMEDAD RELATIVA
    if UltimoDato.HR[0] != np.nan:
        HuRel = HuRel[:18] + str(UltimoDato.HR[0]) + "%"
    #PRECIPITACION ACUMULADA
    if UltimoDato.PPmm[0] != np.nan:
        Preci = Preci[:25] + str(UltimoDato.PPmm[0]) + "mm"
    #RADIACION
    if UltimoDato.RAD[0] != np.nan:
        Radia = Radia[:11] + str(UltimoDato.RAD[0]) + "W/m^2"
    #Viento
    if (UltimoDato.ViMS[0] != np.nan) & (UltimoDato.Dir[0] != np.nan):
        VeloV = VeloV[:22] + (str(np.around(UltimoDato.ViMS[0],1)) + "m/s " + str(np.around(UltimoDato.Dir[0] * 360 / np.pi / 2, 2)) +
                              '° [' + str(np.around(UltimoDato.ViMS[0] * 3.6, 2)) + "km/h del " +
                                VientoSectores(np.around(UltimoDato.Dir[0] * 360 / np.pi / 2, 2)) + "] ")
    return HoraD, TempA, TempS, Press, VeloV, HuRel, Preci, Radia

def GenerarDF(dia= pd.to_datetime('today')):
    fin = dia._date_repr + ' 23:59'
    if dia._date_repr == pd.to_datetime('today')._date_repr:
        fin = pd.to_datetime('today')
    x = pd.date_range( start=dia._date_repr, end=fin, freq='T')
    y = np.sin(2*np.pi*x.minute/60)*1+5
    z = np.cos(2*np.pi*x.minute/60)*10*np.sin(2*np.pi*x.hour/24)+12
    p = (y * z)**8 / 5.50
    h = y * 2
    ppmm = np.sin(2*np.pi*x.minute/360)**2
    r = y
    ang = np.linspace(0, np.pi * 2, len(x), endpoint=False)
    return pd.DataFrame(data={'DateTime': x, 'TempA': y, 'TempS': z, 'Pres': p, 'HR': h, 'ViMS': r, 'Dir': ang, 'PPmm': ppmm})

def DataFrameFromFile( dia= pd.to_datetime('today')):
    archivo = os.path.join(dirDatos, str(dia.year), 'USH' + dia._date_repr + '.csv')
    try:
        df_aux = pd.read_csv(archivo, sep=',')
    except:
        df_aux = GenerarDF(dia)
        #df_aux.set_index(['DateTime'], inplace=True)
        #return df_aux
    #print (df_aux.columns)
    df_aux.rename({'TambC': 'TempA', 'Hr%': 'HR', 'PrhPa': 'Pres', 'VdGrad': 'Dir'}, axis=1, inplace=True)  # new method
    df_aux.Dir = df_aux.Dir * 2 * np.pi / 360
    if not('TempS' in df_aux.columns):
        df_aux['TempS'] = df_aux.TempA - np.nan #
    if not('RadWm2' in df_aux.columns):
        df_aux['RadWm2'] = df_aux.HR - np.nan
    df_aux.DateTime = pd.to_datetime(df_aux.DateTime)
    df_aux.set_index(['DateTime'], inplace=True)
    return df_aux

if __name__ == '__main__':
    Dia = GenerarDF()

    #fig, ax = grafTempSNS(Dia)
    #fig, ax = grafHR(Dia)
    #fig, ax = grafPres(Dia)
    #fig, ax = grafViento(Dia)
    #conjuntoGraf()
    plt.show()
