from PIL.Image import ImagePointHandler
import pandas as pd
from tkinter import Tk
from modulos import busqueda_dr
import gspread
from apoyo.elemetos_de_GUI import Cuadro, Ventana, CustomHovertip
from apoyo.manejo_de_bases import Base_de_datos
from apoyo.vsf import Vitrina_vista
from tkinter import messagebox
import apoyo.datos_frecuentes as dfrec

# Valores de lista desplegable
tipo_ingreso = ('DIRECTO', 'DERIVACION-SUBDIRECCION', 
                'DERIVACION-SUPERVISION', 'DERIVACION-SINADA')
tipo_documento = ('OFICIO', 'MEMORANDO', 'CARTA', 'OFICIO CIRCULAR','MEMORANDO CIRCULAR', 'CARTA CIRCULAR',
                  'INFORME', 'RESOLUCIÓN', 'CÉDULA DE NOTIFICACIÓN', 'INFORME MÚLTIPLE', 'OTROS')
especialista = ('Zurita, Carolina', 'López, José')
tipo_indicacion = ('No corresponde', 'Archivar', 'Actualizar', 'Crear')
si_no = ('Si', 'No')
tipo_respuesta = ('Ejecutó supervisión','Solicitó información a administrado',
                  'Ejecutó acción de evaluación', 'Inició PAS', 'Administrado en adecuación / formalización',
                  'Programó supervisión', 'Programó acción de evaluación', 'No es competente',
                  'No corresponde lo solicitado', 'En evaluación de la EFA', 'Otros')
categorias = ('Pedido de información', 'Pedido de información adicional', 'Pedido de información urgente',
              'Reiterativo', 'Oficio a OCI')
marco_pedido = ('EFA', 'OEFA',
                'Colaboración', 'Delegación', 'Conocimiento')

# Bases de datos principales
b_efa = Base_de_datos('1pjHXiz15Zmw-49Nr4o1YdXJnddUX74n7Tbdf5SH7Lb0', 'Directorio')
b_dr = Base_de_datos('13EgFGcKnHUomMtjBlgZOlPIg_cb4N3aGpkYH13zG6-4', 'DOC_RECIBIDOS')
b_dr_cod = Base_de_datos('13EgFGcKnHUomMtjBlgZOlPIg_cb4N3aGpkYH13zG6-4', 'DOCS_R')
b_dr_hist = Base_de_datos('13EgFGcKnHUomMtjBlgZOlPIg_cb4N3aGpkYH13zG6-4', 'HISTORIAL_DR')
# Bases de datos complementarias
b_de = Base_de_datos('13EgFGcKnHUomMtjBlgZOlPIg_cb4N3aGpkYH13zG6-4', 'DOC_EMITIDOS')
b_ep = Base_de_datos('13EgFGcKnHUomMtjBlgZOlPIg_cb4N3aGpkYH13zG6-4', 'EXTREMOS')

class Doc_recibidos_vista(Ventana):
    """"""
    
    #----------------------------------------------------------------------
    def __init__(self, *args, nuevo=True, lista=None):
        """Constructor"""

        Ventana.__init__(self, *args)

        self.nuevo = nuevo

        # Lista de DE
        tabla_de_de_completa = b_de.generar_dataframe()
        tabla_de_de_id =  tabla_de_de_completa.drop(['Fecha proyecto final', 'Fecha de firma', 'Tipo de documento',
                                                     'Marco de pedido', '¿Se emitió documento?'], axis=1)
        # Lista de DE asociados
        tabla_de_de = tabla_de_de_id.drop(['ID_DE', 'ID_DR', 'ID_EP'], axis=1)
        tabla_de_de_nuevo = tabla_de_de.iloc[100:,]
        # Lista de EP
        tabla_de_ep_completa = b_ep.generar_dataframe()
        tabla_de_ep_id = tabla_de_ep_completa
        tabla_de_ep = tabla_de_ep_id.drop(['ID_DE', 'ID_DR', 'ID_EP'], axis=1)
        tabla_de_ep_nuevo = tabla_de_ep.iloc[100:,]

        # Desplegable EFA
        tabla_directorio = b_efa.generar_dataframe()
        lista_efa = list(set(tabla_directorio['Entidad u oficina']))

        # Labels and Entries
        rejilla_dr = (
            ('L', 0, 0, 'HT entrante'),
            ('E', 0, 1),

            ('L', 0, 2, 'Vía de recepción'),
            ('CX', 0, 3, tipo_ingreso),

            ('L', 1, 0, 'Fecha de recepción OEFA'),
            ('D', 1, 1),

            ('L', 1, 2, 'Fecha de recepción SEFA'),
            ('D', 1, 3),

            ('L', 2, 0, 'Tipo de documento'),
            ('CX', 2, 1, tipo_documento),

            ('L', 2, 2, 'N° de documento'),
            ('E', 2, 3),

            ('L', 3, 0, 'Remitente'),
            ('CX', 3, 1, lista_efa),

            ('L', 3, 2, 'Especialista asignado'),
            ('CX', 3, 3, especialista),

            ('L', 4, 0, 'Asunto'),
            ('EL', 4, 1, 112),

            ('L', 5, 0, 'Aporte del documento'),
            ('EL', 5, 1, 112),

            ('L', 6, 0, 'Indicación'),
            ('CX', 6, 1, tipo_indicacion),

            ('L', 6, 2, '¿Es respuesta?'),
            ('CX', 6, 3, si_no),

            ('L', 7, 0, 'Respuesta'),
            ('CX', 7, 1, tipo_respuesta)
        )

        # Ubicaiones
        # Frame de Título
        self.c0 = Cuadro(self)
        self.c0.agregar_imagen(0,0,'Logo_OSPA.png',202,49)
        self.c0.agregar_titulo(0,1,'                             ')
        self.c0.agregar_titulo(0,2,'Detalle de documento recibido')
        self.c0.agregar_titulo(0,3,'                             ')
        self.c0.agregar_titulo(0,4,'                             ')
        # 1er Frame
        self.c1 = Cuadro(self)
        self.c1.agregar_rejilla(rejilla_dr)

        if self.nuevo != True:
            self.lista_para_insertar = lista
            self.c1.insertar_lista_de_datos(self.lista_para_insertar)


        # 2do Frame
        c2 = Cuadro(self)
        c2.agregar_button(0,1,'Guardar', self.enviar_dr)
        
        # 3er Frame
        c3 = Cuadro(self)
        c3.agregar_button(0, 0,'(+) Agregar', self.busqueda_dr)
        c3.agregar_titulo(0, 1,'                                                       ')
        c3.agregar_titulo(0, 2, 'Documentos emitidos asociados')
        c3.agregar_titulo(0, 3,'                              ')
        c3.agregar_titulo(0, 4,'                              ')
        if self.nuevo != True:
            lista_para_filtrar = lista
            id_doc = lista_para_filtrar[0]
            tabla_de_de_vinculada = tabla_de_de_id[tabla_de_de_id['ID_DR']==id_doc]
            tabla_de_de = tabla_de_de_vinculada.drop(['ID_DE', 'ID_DR', 'ID_EP'], axis=1)
            v1 = Vitrina_vista(self, tabla_de_de, self.ver_de, 
                               self.funcion_de_prueba, height=80, width=1050)  
        else:
            v1 = Vitrina_vista(self, tabla_de_de_nuevo, self.ver_de, 
                               self.funcion_de_prueba, height=80, width=1050)

        # 4to Frame
        c4 = Cuadro(self)
        c4.agregar_button(0, 0,'(+) Agregar', self.busqueda_dr)
        c4.agregar_titulo(0, 1,'                                                       ')
        c4.agregar_titulo(0, 2, 'Extremo de problemas asociados')
        c4.agregar_titulo(0, 3,'                              ')
        c4.agregar_titulo(0, 4,'                              ')

        if self.nuevo != True:
            v2 = Vitrina_vista(self, tabla_de_ep, self.ver_de, 
                               self.funcion_de_prueba, height=80, width=1050)
        else:
            v2 = Vitrina_vista(self, tabla_de_ep_nuevo, self.ver_de, 
                               self.funcion_de_prueba, height=80, width=1050)  
    
    
     #----------------------------------------------------------------------
    def enviar_dr(self):
        """"""
        datos_ingresados = self.c1.obtener_lista_de_datos()

        # Pestaña 1: Código Único
        codigo_ht = datos_ingresados[0]
        b_dr_cod.agregar_datos_generando_codigo(codigo_ht)
        
        # Pestaña 2: 
        lista_descargada_codigo = b_dr_cod.listar_datos_de_fila(codigo_ht)
        codigo_dr = lista_descargada_codigo[0]
        lista_a_cargar = datos_ingresados + [codigo_dr]
        b_dr.agregar_datos(lista_a_cargar)

        # Pestaña 3
        hora_de_creacion = lista_descargada_codigo[1]
        lista_historial = lista_a_cargar + [hora_de_creacion]
        b_dr_hist.agregar_datos(lista_historial)
        
        # Confirmación de registro
        messagebox.showinfo("¡Excelente!", "El registro se ha ingresado correctamente")

    #----------------------------------------------------------------------
    def ver_de(self, x):
        """"""
        
        self.x = x
        texto_documento = 'Documento emitido: ' + x

        lb1 = b_de.listar_datos_de_fila(self.x)
        lista_para_insertar = [lb1[1],lb1[2],lb1[3], lb1[4], lb1[5], 
                               lb1[6], lb1[7], lb1[8], lb1[9], lb1[10], lb1[11]]
        
        self.desaparecer()
        subframe = Doc_emitidos_vista(self, 600, 1100, texto_documento, nuevo=False, lista=lista_para_insertar)
    
    #----------------------------------------------------------------------
    def funcion_de_prueba(self, x):
        """"""
        print(x)

    #----------------------------------------------------------------------
    def ir_a_busqueda_ep(self):
        """"""
        #self.desaparecer()
        #subframe = Pantalla_de_busqueda_ep(self, 500, 400, 'Búsqueda de extremos de problemas')

        #----------------------------------------------------------------------

    def busqueda_dr(self):
        """"""
        self.desaparecer()
        # LargoxAncho
        subFrame = busqueda_dr.Doc_recibidos_busqueda(self, 600, 1200, "Pantalla de búsqueda")



class Doc_emitidos_vista(Ventana):
    """"""
    
    #----------------------------------------------------------------------
    def __init__(self, *args, nuevo=True, lista=None):
        """Constructor"""

        Ventana.__init__(self, *args)

        self.nuevo = nuevo

        # Desplegable EFA
        tabla_directorio = b_efa.generar_dataframe()
        lista_efa = list(set(tabla_directorio['Entidad u oficina']))

        # Labels and Entries
        rejilla_dr = (
            ('L', 0, 0, 'HT de salida'),
            ('E', 0, 1),

            ('L', 0, 2, 'Categoría'),
            ('CX', 0, 3, categorias),

            ('L', 1, 0, 'Fecha de proyecto final'),
            ('D', 1, 1),

            ('L', 1, 2, 'Fecha de firma'),
            ('D', 1, 3),

            ('L', 2, 0, 'Tipo de documento'),
            ('CX', 2, 1, tipo_documento),

            ('L', 2, 2, 'N° de documento'),
            ('E', 2, 3),

            ('L', 3, 0, 'Destinatario'),
            ('CX', 3, 1, lista_efa),

            ('L', 3, 2, '¿Se emitió documento?'),
            ('CX', 3, 3, si_no),

            ('L', 4, 0, 'Detalle de requerimiento'),
            ('EL', 4, 1, 112),

            ('L', 5, 0, 'Marco de pedido'),
            ('CX', 5, 1, marco_pedido),

            ('L', 5, 2, 'Fecha de notificación'),
            ('D', 5, 3)

        )

        # Lista de DR
        tabla_de_dr = b_dr.generar_dataframe()
        tabla_de_dr = tabla_de_dr.drop(['ID_DE', 'ID_DR', 'ID_EP', 'Via de recepción',
                                        'Fecha de ingreso OEFA', 'Tipo de documento', 'Especialista',
                                        'Indicación', '¿Es respuesta?', 'Respuesta'], axis=1)
        # Lista de EP
        tabla_de_ep = b_ep.generar_dataframe()
        tabla_de_ep = tabla_de_ep.drop(['ID_DE', 'ID_DR', 'ID_EP'], axis=1)

        # Ubicaiones
        # Frame de Título
        self.c0 = Cuadro(self)
        self.c0.agregar_imagen(0,0,'Logo_OSPA.png',202,49)
        self.c0.agregar_titulo(0,1,'                             ')
        self.c0.agregar_titulo(0,2,'Detalle de documento emitido ')
        self.c0.agregar_titulo(0,3,'                             ')
        self.c0.agregar_titulo(0,4,'                             ')
        # 1er Frame
        self.c1 = Cuadro(self)
        self.c1.agregar_rejilla(rejilla_dr)

        if self.nuevo != True:
            self.lista_para_insertar = lista
            self.c1.insertar_lista_de_datos(self.lista_para_insertar)

        # 2do Frame
        c2 = Cuadro(self)
        c2.agregar_button(1,1,'Guardar', self.enviar_de)

        # 3er Frame
        c3 = Cuadro(self)
        c3.agregar_titulo(2,0,'Extremo de problemas asociados')
        if self.nuevo != True:
            v1 = Vitrina_vista(self, tabla_de_ep, self.ver_dr, 
                               self.funcion_de_prueba, height=80, width=1050)

        # 4to Frame
        c4 = Cuadro(self)
        c4.agregar_button(0, 0,'(+) Agregar', self.busqueda_dr)
        c4.agregar_titulo(0, 1,'                                                       ')
        c4.agregar_titulo(0, 2, 'Documentos recibidos asociados')
        c4.agregar_titulo(0, 3,'                              ')
        c4.agregar_titulo(0, 4,'                              ')
        if self.nuevo != True:
            v2 = Vitrina_vista(self, tabla_de_dr, self.ver_dr, 
                               self.funcion_de_prueba, height=80, width=1050)  
        
        
    #----------------------------------------------------------------------
    def funcion_de_prueba(self, x):
        """"""
        print(x)

     #----------------------------------------------------------------------
    def enviar_de(self):
        """"""
        datos_ingresados = self.c1.obtener_lista_de_datos()
        b0 = Base_de_datos('13EgFGcKnHUomMtjBlgZOlPIg_cb4N3aGpkYH13zG6-4', 'DOCS_R')
        codigo = datos_ingresados[0]
        b0.agregar_datos_generando_codigo(codigo)
        
        # Confirmación de registro
        messagebox.showinfo("¡Excelente!", "El registro se ha ingresado correctamente")

    #----------------------------------------------------------------------
    def ver_dr(self, x):
        """"""
        self.x = x
        texto_documento = 'Documento recibido: ' + x

        b1 = Base_de_datos('13EgFGcKnHUomMtjBlgZOlPIg_cb4N3aGpkYH13zG6-4', 'DOC_RECIBIDOS')
        lb1 = b1.listar_datos_de_fila(self.x)
        lista_para_insertar = [lb1[1], lb1[2],lb1[3], lb1[4], lb1[5], 
                               lb1[6], lb1[7], lb1[8], lb1[9], lb1[10], lb1[11], lb1[12], lb1[13]]
        
        self.desaparecer()
        subframe = Doc_recibidos_vista(self, 600, 1100, texto_documento, nuevo=False, lista=lista_para_insertar)

    #----------------------------------------------------------------------
    def ir_a_vista_ep(self):
        """"""
        #self.desaparecer()
        #subframe = Pantalla_de_vista_ep(self, 500, 400, 'Búsqueda de extremos de problemas')

        #----------------------------------------------------------------------

    def busqueda_dr(self):
        """"""
        #self.desaparecer()
        # LargoxAncho
        #subFrame = busqueda_dr.Doc_recibidos_busqueda(self, 600, 1200, "Pantalla de búsqueda")
