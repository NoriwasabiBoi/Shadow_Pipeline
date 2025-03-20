from PySide2 import QtWidgets, QtCore, QtGui
import re
import hou


class WorkItems:
    def __init__(self):
        super().__init__()
        selected_nodes = hou.selectedNodes()
        if not selected_nodes:
            hou.ui.displayMessage("No hay nodos seleccionados.")
            raise ValueError("No hay nodos seleccionados.")

        self.node = selected_nodes[0]
        self.parent = self.node.parent()
        self.geo = self.node.geometry()
        if not self.geo:
            raise ValueError("El nodo seleccionado no tiene geometría.")

        self.att_name = []
        self.att_material = []
        self.point_groups = []
        self.vertex_groups = []
        self.prim_groups = []

        merge_name = "merge_all"
        self.merge = self.parent.node(merge_name) or self.parent.createNode("merge", merge_name)

    def validate_attributes(self):
        """
        Valida que los atributos necesarios existan en la geometría.
        """
        if not self.geo.findPrimAttrib("name"):
            raise ValueError("El atributo 'name' no existe en los primitivos.")
        if not self.geo.findPrimAttrib("shop_materialpath"):
            raise ValueError("El atributo 'shop_materialpath' no existe en los primitivos.")

    def initialize_attributes(self):
        """
        Valida los atributos y llena las listas necesarias.
        """
        self.validate_attributes()
        self.att_name = list(set(self.geo.primStringAttribValues("name")))

        self.att_material = list(set(self.geo.primStringAttribValues("shop_materialpath")))

    def pointgroup(self):
        self.point_groups = list(set(self.geo.pointGroups()))
        point_list = [i.name() for i in self.point_groups]
        return point_list

    def vertexgroup(self):
        self.vertex_groups = list(set(self.geo.vertexGroups()))
        vertex_list = [i.name() for i in self.vertex_groups]
        return vertex_list

    def primgroup(self):
        self.prim_groups = list(set(self.geo.primGroups()))
        prim_list = [i.name() for i in self.prim_groups]
        return prim_list

    def generate_group(self, name):

        names = name

        for i in names:
            sanitized = re.sub(r'[^\w]', '_', i.name())
            if sanitized[0].isdigit():  # Si comienza con un número, añadir prefijo
                sanitized = f"n_{sanitized}"
            blast_name = f"{sanitized}"

            # Verificar si ya existe el nodo blast
            blast = self.parent.node(blast_name)
            if blast:
                print(f"El nodo '{blast_name}' ya existe.")
            else:
                #                print(f"Creando el nodo '{blast_name}'...")
                blast = self.node.createOutputNode("blast", blast_name)
                blast.parm("group").set(blast_name)
                blast.parm("negate").set(True)
                self.merge.setNextInput(blast)

        self.parent.layoutChildren()

    def satinized(self, list, att):

        list_value = [i for i in list if i.strip()]

        att = att

        for i in list_value:
            # Sanitizar el nombre
            sanitized = re.sub(r'[^\w]', '_', i)
            if sanitized[0].isdigit():  # Si comienza con un número, añadir prefijo
                sanitized = f"n_{sanitized}"
            blast_name = f"{sanitized}"

            # Verificar si ya existe el nodo blast
            blast = self.parent.node(blast_name)
            if blast:
                print(f"El nodo '{blast_name}' ya existe.")
            else:
                #                print(f"Creando el nodo '{blast_name}'...")
                blast = self.node.createOutputNode("blast", blast_name)
                blast.parm("group").set(f'@{att}={i}')
                blast.parm("negate").set(True)
                self.merge.setNextInput(blast)

    def split_name(self):

        self.satinized(self.att_name, "name")
        self.parent.layoutChildren()

    def split_shop_material(self):

        self.satinized(self.att_material, "shop_materialpath")
        self.parent.layoutChildren()

    def split_custom(self, custom_attr):
        """
        Divide la geometría en función de un atributo personalizado y crea nodos Blast.
        """
        # Verificar si el atributo existe
        if not self.geo.findPrimAttrib(custom_attr):
            print(f"Error: El atributo '{custom_attr}' no existe en los primitivos.")
            return

        # Obtener valores únicos del atributo
        custom_list = list(set(self.geo.primStringAttribValues(custom_attr)))
        custom_list = [i for i in custom_list if i.strip()]  # Filtrar valores vacíos

        #        self.satinized(custom_list, custom_attr)

        self.parent.layoutChildren()

    def split_point_group(self):

        self.generate_group(self.point_groups)
        self.parent.layoutChildren()

    def split_vertex_group(self):

        self.generate_group(self.vertex_groups)
        self.parent.layoutChildren()

    def split_prim_group(self):

        self.generate_group(self.prim_groups)
        self.parent.layoutChildren()


## Ejecutar
# a = WorkItems()
# a.split_prim_group()


class Main(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.split = WorkItems()

        self.setWindowTitle("Super Split")
        self.setGeometry(400, 100, 400, 100)
        self.list_sel_value = ["Name", "Material", "Group", "Custom_ATT"]

        self.add_widgets()

    def add_widgets(self):

        main_layout = QtWidgets.QVBoxLayout()
        h_layout = QtWidgets.QHBoxLayout()
        self.h_check_widget = QtWidgets.QWidget()
        self.h_list_widget = QtWidgets.QWidget()
        self.h_check_layout = QtWidgets.QHBoxLayout(self.h_check_widget)
        h_button_layout = QtWidgets.QHBoxLayout()

        list_layout = QtWidgets.QVBoxLayout(self.h_list_widget)

        ##############__h_Layout_Widgets###################

        self.ledit = QtWidgets.QLineEdit()
        self.ledit.setPlaceholderText("if custom att selection... Write the custom ATTRIBUTE")
        self.ledit.setVisible(False)

        self.cbox = QtWidgets.QComboBox()
        self.cbox.setContentsMargins(110, 110, 110, 110)
        self.cbox.currentIndexChanged.connect(self.selectionCheck)
        self.cbox.addItems(self.list_sel_value)
        self.ledit.setVisible(False)

        h_layout.addWidget(self.cbox)
        h_layout.addWidget(self.ledit)

        h_layout.setSpacing(2)
        h_layout.setContentsMargins(0, 0, 0, 0)

        ##############__h_button_Widgets###################

        button_split = QtWidgets.QPushButton("Split")
        button_split.setBaseSize(50, 20)
        button_split.clicked.connect(self.split_node)
        h_button_layout.addWidget(button_split)

        h_button_layout.setSpacing(50)
        h_button_layout.setAlignment(QtCore.Qt.AlignHCenter)
        # h_button_layout.setContentsMargins(110, 30, 30, 80)

        ##############__h_checks_Widgets###################

        self.check_1 = QtWidgets.QCheckBox("Points")
        self.check_2 = QtWidgets.QCheckBox("Vertex")
        self.check_3 = QtWidgets.QCheckBox("Prims")

        self.check_1.stateChanged.connect(lambda: self.check_toggle(self.check_1))
        self.check_2.stateChanged.connect(lambda: self.check_toggle(self.check_2))
        self.check_3.stateChanged.connect(lambda: self.check_toggle(self.check_3))

        self.h_check_layout.addWidget(self.check_1)
        self.h_check_layout.addWidget(self.check_2)
        self.h_check_layout.addWidget(self.check_3)

        self.h_check_layout.setSpacing(1)
        self.h_check_layout.setAlignment(QtCore.Qt.AlignAbsolute)
        h_button_layout.setAlignment(QtCore.Qt.AlignTop)

        # h_button_layout.setAlignment(QtCore.Qt.AlignTop)
        # h_check_layout.setAlignment(QtCore.Qt.AlignAbsolute)

        self.h_check_widget.setVisible(False)

        # h_button_layout.setAlignment(QtCore.Qt.AlignTop)

        self.list_groups = QtWidgets.QListWidget()
        self.list_groups.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        list_layout.addWidget(self.list_groups)
        self.h_list_widget.setVisible(False)

        # Agregar los layouts al layout principal
        main_layout.addLayout(h_layout)
        main_layout.addWidget(self.h_check_widget)  # Agregar el contenedor
        main_layout.addLayout(h_button_layout)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.h_list_widget)

        self.setLayout(main_layout)

    def selectionCheck(self, index):
        selected_item = self.cbox.currentText().lower()  # Obtiene el texto seleccionado del combo box

        # Mostrar/ocultar el layout de checkboxes según el valor seleccionado
        if selected_item == "group":

            self.h_check_widget.setVisible(True)  # Muestra el layout de checkboxes
            self.h_list_widget.setVisible(True)
        else:
            self.h_list_widget.setVisible(False)
            self.h_check_widget.setVisible(False)  # Oculta el layout de checkboxes

        if selected_item == "custom_att":

            self.ledit.setVisible(True)
        else:
            self.ledit.setVisible(False)

        self.update()

    def check_toggle(self, checkbox):
        list_split = self.split

        if checkbox.isChecked():
            self.list_groups.setVisible(True)
            self.check_1.setChecked(checkbox == self.check_1)
            self.check_2.setChecked(checkbox == self.check_2)
            self.check_3.setChecked(checkbox == self.check_3)
            self.list_groups.clear()
            if checkbox.text().lower() == "points":
                self.list_groups.addItems(list_split.pointgroup())
            elif checkbox.text().lower() == "vertex":
                self.list_groups.addItems(list_split.vertexgroup())
            elif checkbox.text().lower() == "prims":
                self.list_groups.addItems(list_split.primgroup())

            self.check_name = checkbox.text().lower()

    def split_node(self):
        try:

            self.split.initialize_attributes()  # Asegura que las listas estén llenas
            selected_item = self.cbox.currentText().lower()
            att = self.ledit.text().strip()  # Captura el texto de ledit (si es necesario)

            if selected_item == "name":
                self.split.split_name()

            elif selected_item == "group":
                selected_groups = [item.text() for item in
                                   self.list_groups.selectedItems()]  # Obtener los grupos seleccionados
                if self.check_name == "prims":
                    self.split.generate_group([g for g in self.split.prim_groups if g.name() in selected_groups])
                elif self.check_name == "points":
                    self.split.generate_group([g for g in self.split.point_groups if g.name() in selected_groups])
                elif self.check_name == "vertex":
                    self.split.generate_group([g for g in self.split.vertex_groups if g.name() in selected_groups])


            elif selected_item == "material":
                self.split.split_shop_material()

            elif selected_item == "custom_att":
                if not att:  # Validación del atributo personalizado
                    hou.ui.displayMessage("Por favor, ingresa un atributo personalizado válido.")
                    return
                self.split.split_custom(att)

            else:
                hou.ui.displayMessage("Selección inválida.")

        except ValueError as e:
            hou.ui.displayMessage(str(e))  # Muestra mensajes de error al usuario
        except Exception as e:
            hou.ui.displayMessage(f"Error inesperado: {str(e)}")

        # if __name__ == '__main__':


#    app = QtWidgets.QApplication([])


window = Main()
window.show()
# window.showMaximized()

#    app.exec_()