# -*- coding: utf-8 -*-
from sys import exit
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from capture_core import *
# 使用matplotlib绘制柱状图
import numpy as np
import matplotlib.pyplot as plt
import json
from monitor_system import start_monitor
from multiprocessing import Process



class Ui_MainWindow(QMainWindow):

    core = None
    timer = None
    Monitor = None
    Forged = None

    def setbg(self):
        palette = QPalette()
        pix = QPixmap("img/bg10_1.jpg") #5,10,11,12
        pix = pix.scaled(self.width(), self.height())
        palette.setBrush(QPalette.Background, QBrush(pix))
        self.setPalette(palette)

    def setupUi(self):
        self.setWindowTitle("Network_monitoring")
        self.resize(1200, 750)
        self.setbg()

        #设置程序图标
        icon = QIcon()
        icon.addPixmap(QPixmap("img/logo.ico"), QIcon.Normal, QIcon.Off)#修改图标
        self.setWindowIcon(icon)
        self.setIconSize(QSize(20, 20))
        #中间布局，设为透明
        self.centralWidget = QWidget(self)
        self.centralWidget.setStyleSheet("background:transparent;")

        #栅栏布局，使得窗口自适应
        self.gridLayout = QGridLayout(self.centralWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setSpacing(6)

        #顶部控件布局
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setContentsMargins(10, 2, 10, 1)
        self.horizontalLayout.setSpacing(20)

        #三个显示区布局
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setContentsMargins(10, 0, 3, 10)
        self.verticalLayout.setSpacing(6)

        # 初始主窗口字体
        font = QFont()
        with open('data.json', 'r') as file_obj:
            '''读取json文件'''
            old_font = json.load(file_obj)  # 返回列表数据，也支持字典
        if old_font["font"]:
            font.setFamily(old_font["font"])
            font.setPointSize(int(old_font["size"]))
        else:
            if platform == 'Windows':
                font.setFamily("Microsoft YaHei")
                old_font["font"] = "Microsoft YaHei"
            if platform == "Linux":
                font.setFamily("Noto Mono")
                old_font["font"] = "Noto Mono"
            font.setPointSize(11)
            with open('data.json', 'w') as file_obj:
                '''写入json文件'''
                json.dump(old_font, file_obj)

        #数据包显示框
        self.info_tree = QTreeWidget(self.centralWidget)
        self.info_tree.setFrameStyle(QFrame.Box | QFrame.Plain)
        self.info_tree.setAutoScroll(True)
        self.info_tree.setRootIsDecorated(False)
        self.info_tree.setFont(font)
        self.info_tree.setColumnCount(7)  #设置表格为7列
        #固定行高，取消每次刷新所有行，避免更新数据时不流畅
        self.info_tree.setUniformRowHeights(True)
        #设置表头
        self.info_tree.headerItem().setText(0, "No.")
        self.info_tree.headerItem().setText(1, "Time")
        self.info_tree.headerItem().setText(2, "Source")
        self.info_tree.headerItem().setText(3, "Destination")
        self.info_tree.headerItem().setText(4, "Protocol")
        self.info_tree.headerItem().setText(5, "Length")
        self.info_tree.headerItem().setText(6, "Info")
        self.info_tree.setStyleSheet("background:transparent;")
        self.info_tree.setSortingEnabled(True)
        self.info_tree.sortItems(0, Qt.AscendingOrder)
        self.info_tree.setColumnWidth(0, 75)
        self.info_tree.setColumnWidth(1, 130)
        self.info_tree.setColumnWidth(2, 150)
        self.info_tree.setColumnWidth(3, 180)
        self.info_tree.setColumnWidth(4, 140)
        self.info_tree.setColumnWidth(5, 100)
        for i in range(7):
            self.info_tree.headerItem().setBackground(i,QBrush(QColor(Qt.white)))
        self.info_tree.setSelectionBehavior(QTreeWidget.SelectRows)  #设置选中时为整行选中
        self.info_tree.setSelectionMode(QTreeWidget.SingleSelection)  #设置只能选中一行
        """显示排序图标"""
        self.info_tree.header().setSortIndicatorShown(True)
        self.info_tree.clicked.connect(self.on_tableview_clicked)

        #数据包详细内容显示框
        self.treeWidget = QTreeWidget(self.centralWidget)
        self.treeWidget.setAutoScroll(True)
        self.treeWidget.setTextElideMode(Qt.ElideMiddle)
        self.treeWidget.header().setStretchLastSection(True)
        self.treeWidget.setStyleSheet("background:transparent; color:black;")
        self.treeWidget.setStyleSheet("color:black;")
        self.treeWidget.header().hide()
        self.treeWidget.setFont(font)
        # 设为只有一列
        self.treeWidget.setColumnCount(1)
        self.treeWidget.setFrameStyle(QFrame.Box | QFrame.Plain)

        #hex显示区域
        self.hexBrowser = QTextBrowser(self.centralWidget)
        self.hexBrowser.setText("")
        self.hexBrowser.setFont(font)
        self.hexBrowser.setStyleSheet("color:white;")
        self.hexBrowser.setStyleSheet("background:transparent;  color:white;")
        self.hexBrowser.setFrameStyle(QFrame.Box | QFrame.Plain)

        # 允许用户通过拖动三个显示框的边界来控制子组件的大小
        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.addWidget(self.info_tree)
        self.splitter.addWidget(self.treeWidget)
        self.splitter.addWidget(self.hexBrowser)
        self.verticalLayout.addWidget(self.splitter)

        self.gridLayout.addLayout(self.verticalLayout, 1, 0, 1, 1)

        '''
        #过滤器输入框
        self.Filter = QLineEdit(self.centralWidget)
        self.Filter.setPlaceholderText("Apply a capture filter … ")
        self.Filter.setStyleSheet("background:#ADD8E6")
        self.Filter.setFont(font)
        self.horizontalLayout.addWidget(self.Filter)
        '''

        string_list = ["tcp port 80","not icmp","dst net 10.63"]
        self.Filter = QComboBox(self.centralWidget)
        self.Filter.addItems(string_list)
        self.Filter.setEditable(True)
        self.Filter.setCurrentIndex(-1)
        self.Filter.setInsertPolicy(QComboBox.InsertAtTop)
        self.Filter.setMaxCount(8)
        self.Filter.completer()
        self.Filter.setStyleSheet("background:#FAF0E6;min-height: 35px; ")
        self.horizontalLayout.addWidget(self.Filter)



        #过滤器按钮
        self.FilterButton = QPushButton(self.centralWidget)
        self.FilterButton.setText("过滤搜索")
        icon1 = QIcon()
        icon1.addPixmap(QPixmap("img/search.png"), QIcon.Normal, QIcon.Off)
        self.FilterButton.setIcon(icon1)
        self.FilterButton.setFixedSize(100,35)
        self.FilterButton.setIconSize(QSize(20, 20))
        #self.FilterButton.setStyleSheet("background:white")
        self.FilterButton.setStyleSheet( "QPushButton{color: white}" #按键前景色
                                 "QPushButton{background-color:#CD5C5C;order-style: outset;border-width: 1px;border-radius: 10px;border-color: beige;font: bold 14px;min-width: 8em;padding: 6px;}"  #按键背景色
                                 "QPushButton:hover{color: black}" #光标移动到上面后的前景色
                                 "QPushButton:pressed{background-color: #A52A2A; border: None;}")
        self.FilterButton.clicked.connect(self.on_start_action_clicked)
        self.horizontalLayout.addWidget(self.FilterButton)
        """
           网卡选择框
        """
        self.choose_nicbox = QComboBox(self.centralWidget)
        self.choose_nicbox.setFont(font)
        self.choose_nicbox.setStyleSheet("background:#FAF0E6; color:black;")
        self.horizontalLayout.addWidget(self.choose_nicbox)

        self.horizontalLayout.setStretch(0, 8)
        self.horizontalLayout.setStretch(1, 1)
        self.horizontalLayout.setStretch(2, 4)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        """初始网卡复选框"""
        row_num = len(keys)
        self.choose_nicbox.addItem("All")
        for i in range(row_num):
            self.choose_nicbox.addItem(keys[i])

        self.setCentralWidget(self.centralWidget)
        """
           顶部菜单栏
        """
        self.menuBar = QMenuBar(self)
        self.menuBar.setGeometry(QRect(0, 0, 953, 23))
        self.menuBar.setAccessibleName("")
        self.menuBar.setStyleSheet('''
            QMenu {
                background-color:rgb(89,87,87); /*整个背景*/
                border: 3px solid #CD5C5C;/*整个菜单边缘*/
                }
                QMenu::item {
                    font-size: 7pt; 
                    color: rgb(225,225,225);  /*字体颜色*/
                    border: 1px solid rgb(60,60,60);    /*item选框*/
                    background-color:rgb(89,87,87);
                    padding: 10px 9px; /*设置菜单项文字上下和左右的内边距，效果就是菜单中的条目左右上下有了间隔*/
                    margin:1px 1px;/*设置菜单项的外边距*/
                }
                QMenu::item:selected { 
                    background-color:#CD5C5C;/*选中的样式*/
                }
                QMenu::item:pressed {/*菜单项按下效果*/
                    border: 1px solid rgb(60,60,61); 
                    background-color: #A52A2A; 
                }\  
        ''')
        self.menuBar.setDefaultUp(False)

        self.menu_F = QMenu(self.menuBar)
        self.menu_F.setTitle("文件")


        self.capture_menu = QMenu(self.menuBar)
        self.capture_menu.setTitle("捕获")

        self.menu_H = QMenu(self.menuBar)
        self.menu_H.setTitle("帮助")

        self.menu_Analysis = QMenu(self.menuBar)
        self.menu_Analysis.setTitle("分析")

        self.menu_Statistic = QMenu(self.menuBar)
        self.menu_Statistic.setTitle("统计")
        self.setMenuBar(self.menuBar)

        #顶部工具栏
        self.mainToolBar = QToolBar(self)
        self.addToolBar(Qt.TopToolBarArea, self.mainToolBar)
        self.statusBar = QStatusBar(self)
        self.mainToolBar.setStyleSheet("background: #f6ecb6;")
        self.mainToolBar.setFixedHeight(38)
        self.setStatusBar(self.statusBar)

        #开始键
        self.start_action = QAction(self)
        icon2 = QIcon()
        icon2.addPixmap(QPixmap("img/start.png"), QIcon.Normal, QIcon.Off)
        self.start_action.setIcon(icon2)
        self.start_action.setText("开始")
        self.start_action.setShortcut('F1')
        self.start_action.triggered.connect(self.on_start_action_clicked)

        #停止键
        self.stop_action = QAction(self)
        icon3 = QIcon()
        icon3.addPixmap(QPixmap("img/stop.png"), QIcon.Normal, QIcon.Off)
        self.stop_action.setIcon(icon3)
        self.stop_action.setText("停止")
        self.stop_action.setShortcut('F3')
        self.stop_action.setDisabled(True)  #开始时该按钮不可点击
        self.stop_action.triggered.connect(self.on_stop_action_clicked)

        #暂停键
        self.pause_action = QAction(self)
        p_icon = QIcon()
        p_icon.addPixmap(QPixmap("img/terminal.png"), QIcon.Normal, QIcon.Off)
        self.pause_action.setIcon(p_icon)
        self.pause_action.setText("暂停")
        self.pause_action.setShortcut('F2')
        self.pause_action.setDisabled(True)  # 开始时该按钮不可点击
        self.pause_action.triggered.connect(self.on_pause_action_clicked)

        #重新开始键
        self.actionRestart = QAction(self)
        icon4 = QIcon()
        icon4.addPixmap(QPixmap("img/restart.png"), QIcon.Normal, QIcon.Off)
        self.actionRestart.setIcon(icon4)
        self.actionRestart.setText("重新开始")
        self.actionRestart.setShortcut('F4')
        self.actionRestart.setDisabled(True)  # 开始时该按钮不可点击
        self.actionRestart.triggered.connect(self.on_actionRestart_clicked)


        #帮助文档
        # action_readme = QAction(self)
        # action_readme.setText("使用文档")
        action_about = QAction(self)
        icon5 = QIcon()
        icon5.addPixmap(QPixmap("img/about.png"), QIcon.Normal, QIcon.Off)
        action_about.setIcon(icon5)
        action_about.setText("关于")
        action_about.setShortcut("F8")
        action_about.triggered.connect(self.on_action_about_clicked)

        #打开文件键
        action_openfile = QAction(self)
        icon6 = QIcon()
        icon6.addPixmap(QPixmap("img/openfile.png"), QIcon.Normal, QIcon.Off)
        action_openfile.setIcon(icon6)
        action_openfile.setText("打开")
        action_openfile.setShortcut("ctrl+O")
        action_openfile.triggered.connect(self.on_action_openfile_clicked)

        #保存文件键
        action_savefile = QAction(self)
        icon7 = QIcon()
        icon7.addPixmap(QPixmap("img/save.png"), QIcon.Normal, QIcon.Off)
        action_savefile.setIcon(icon7)
        action_savefile.setText("保存")
        action_savefile.setShortcut("ctrl+S")
        action_savefile.triggered.connect(self.on_action_savefile_clicked)



        #流量监测
        self.action_track = QAction(self)
        self.action_track.setText("流量监测")
        self.action_track.setShortcut('F5')
        self.action_track.triggered.connect(self.on_action_track_clicked)

        #IP地址类型统计图
        self.IP_statistics = QAction(self)
        iconip = QIcon()
        iconip.addPixmap(QPixmap("img/ip.png"), QIcon.Normal, QIcon.Off)
        self.IP_statistics.setIcon(iconip)
        self.IP_statistics.setText("IP地址类型统计")
        self.IP_statistics.setShortcut('F6')
        self.IP_statistics.triggered.connect(self.on_IP_statistics_clicked)

        #报文类型统计图
        self.message_statistics = QAction(self)
        iconpkg = QIcon()
        iconpkg.addPixmap(QPixmap("img/pkg.png"), QIcon.Normal, QIcon.Off)
        self.message_statistics.setIcon(iconpkg)
        self.message_statistics.setText("报文类型统计")
        self.message_statistics.setShortcut('F7')
        self.message_statistics.triggered.connect(
            self.on_message_statistics_clicked)
        """
           添加工具栏：开始，暂停，停止，重新开始
        """
        self.mainToolBar.addAction(self.start_action)
        self.mainToolBar.addAction(self.pause_action)
        self.mainToolBar.addAction(self.stop_action)
        self.mainToolBar.addAction(self.actionRestart)

        self.menu_F.addAction(action_openfile)
        self.menu_F.addAction(action_savefile)
        self.menu_F.showFullScreen()

        #捕获菜单栏添加子菜单
        self.capture_menu.addAction(self.start_action)
        self.capture_menu.addAction(self.pause_action)
        self.capture_menu.addAction(self.stop_action)
        self.capture_menu.addAction(self.actionRestart)

        #self.menu_H.addAction(action_readme)
        self.menu_H.addAction(action_about)

        #self.menu_Analysis.addAction(self.forged_action)
        self.menu_Analysis.addAction(self.action_track)

        self.menu_Statistic.addAction(self.IP_statistics)
        self.menu_Statistic.addAction(self.message_statistics)

        self.menuBar.addAction(self.menu_F.menuAction())
        # self.menuBar.addAction(self.edit_menu.menuAction())
        self.menuBar.addAction(self.capture_menu.menuAction())
        self.menuBar.addAction(self.menu_Analysis.menuAction())
        self.menuBar.addAction(self.menu_Statistic.menuAction())
        self.menuBar.addAction(self.menu_H.menuAction())

        # self.statusBar.showMessage('实时更新的信息', 0)  # 状态栏本身显示的信息 第二个参数是信息停留的时间，单位是毫秒，默认是0（0表示在下一个操作来临前一直显示）
        """底部状态栏
            利用self.comNum.setText()实时更新状态栏信息
        """
        self.comNum = QLabel('下载速度：')
        self.baudNum = QLabel('上传速度:')
        self.getSpeed = QLabel('收包速度：')
        self.sendSpeed = QLabel('发包速度：')
        self.netNic = QLabel('From 杨老师的抓包小队')
        self.statusBar.setStyleSheet("background: #EDEDED;")
        """各个单元空间占比"""
        self.statusBar.addPermanentWidget(self.netNic, stretch=2)
        self.statusBar.addPermanentWidget(self.getSpeed, stretch=1)
        self.statusBar.addPermanentWidget(self.sendSpeed, stretch=1)
        self.statusBar.addPermanentWidget(self.comNum, stretch=1)
        self.statusBar.addPermanentWidget(self.baudNum, stretch=1)

        QMetaObject.connectSlotsByName(self)
        self.core = Core(self)
        # 设置定时器将抓包列表置底
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.info_tree.scrollToBottom)
        self.show()

    """
        重写窗口关闭事件
    """

    def closeEvent(self, QCloseEvent):
        def close_to_do():
            self.core.clean_out()
            if self.Monitor and self.Monitor.is_alive():
                self.Monitor.terminate()
            if self.Forged and self.Forged.is_alive():
                self.Forged.terminate()
            exit()

        if self.core.start_flag or self.core.pause_flag:
            # 没有停止抓包
            reply = QMessageBox.question(
                self, 'Message', "您是否要停止捕获，并保存已捕获的分组?\n警告：若不保存，您捕获的分组将会丢失",
                QMessageBox.Save | QMessageBox.Close | QMessageBox.Cancel,
                QMessageBox.Cancel)
            if reply == QMessageBox.Cancel:
                QCloseEvent.ignore()
            if reply == QMessageBox.Close:
                self.core.stop_capture()
                close_to_do()
            elif reply == QMessageBox.Save:
                self.core.stop_capture()
                self.on_action_savefile_clicked()
                close_to_do()
        elif self.core.stop_flag and not self.core.save_flag:
            """
                已停止，但没有保存文件
            """
            reply = QMessageBox.question(
                self, 'Message', "您是否保存已捕获的分组?\n警告：若不保存，您捕获的分组将会丢失",
                QMessageBox.Save | QMessageBox.Close | QMessageBox.Cancel,
                QMessageBox.Cancel)
            if reply == QMessageBox.Cancel:
                QCloseEvent.ignore()
            elif reply == QMessageBox.Save:
                self.on_action_savefile_clicked()
                close_to_do()
            else:
                close_to_do()
        elif self.core.save_flag or not self.core.start_flag:
            """
                未工作状态
            """
            reply = QMessageBox.question(self, 'Message', "您是否要退出本程序?",
                                         QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.No)
            if reply == QMessageBox.Yes:
                close_to_do()
            else:
                QCloseEvent.ignore()


    """
       数据包视图 数据记录点击事件
       点击列表中一条记录时，在下面的frame框中显示帧的详细信息
    """

    def on_tableview_clicked(self):
        selected_row = self.info_tree.currentItem().text(0)  #当前选择的编号
        #表格停止追踪更新
        if selected_row and selected_row.isdigit():
            self.timer.stop()
            self.show_infoTree((int)(selected_row))

    """
        展开帧的详细信息
    """

    def show_infoTree(self, selected_row):
        """
           清空Frame Information内容
        """
        self.treeWidget.clear()
        """
           添加树节点
           Item1: 第一层树节点
           Item1_1: 第二层树节点，Item1的子节点
           QTreeWidgetItem(parentNode, text)   parentNode:父节点  text：当前节点内容
        """
        parentList, childList, hex_dump = self.core.on_click_item(selected_row)
        p_num = len(parentList)
        for i in range(p_num):
            item1 = QTreeWidgetItem(self.treeWidget)
            item1.setText(0, parentList[i])
            c_num = len(childList[i])
            for j in range(c_num):
                item1_1 = QTreeWidgetItem(item1)
                item1_1.setText(0, childList[i][j])
        self.set_hex_text(hex_dump)

    """
       获取当前选择的网卡
    """

    def get_choose_nic(self):
        card = self.choose_nicbox.currentText()
        self.netNic.setText('当前网卡：' + card)
        if (card == 'All'):
            a = None
        elif platform == 'Windows':
            a = netcards[card]
        elif platform == 'Linux':
            a = card
        else:
            a = None
        return a

    """
       设置hex区文本
    """

    def set_hex_text(self, text):
        self.hexBrowser.setText(text)

    """
       开始键点击事件
    """

    def on_start_action_clicked(self):
        if self.core.stop_flag:
            # 重新开始清空面板内容
            self.info_tree.clear()
            self.treeWidget.clear()
            self.set_hex_text("")
        if self.Filter.currentText() != "":
            insertflag = True
            currentT = self.Filter.currentText()
            for i in range(0,self.Filter.count()):
                if currentT == self.Filter.itemText(i):
                    insertflag = False
            if insertflag:
                self.Filter.insertItem(0,currentT)
        self.core.start_capture(self.get_choose_nic(), self.Filter.currentText())
        """
           点击开始后，过滤器不可编辑，开始按钮、网卡选择框全部设为不可选
           激活暂停、停止键、重新开始键
        """
        self.start_action.setDisabled(True)
        self.Filter.setEnabled(False)
        self.FilterButton.setEnabled(False)
        self.choose_nicbox.setEnabled(False)
        self.actionRestart.setDisabled(False)
        self.pause_action.setEnabled(True)
        self.stop_action.setEnabled(True)
        self.timer.start(flush_time)

    """
       暂停事件点击事件
    """

    def on_pause_action_clicked(self):
        self.core.pause_capture()
        """
           激活开始、停止、重新开始键、过滤器、网卡选择框
        """
        self.start_action.setEnabled(True)
        self.stop_action.setDisabled(False)
        self.actionRestart.setDisabled(False)
        self.Filter.setDisabled(True)
        self.FilterButton.setDisabled(True)
        self.choose_nicbox.setDisabled(False)
        self.pause_action.setDisabled(True)
        self.timer.stop()

    """
           菜单栏停止键点击事件
    """

    def on_stop_action_clicked(self):
        self.core.stop_capture()
        """
            激活开始键、重新开始键、过滤器、网卡选择框
        """
        self.stop_action.setDisabled(True)
        self.pause_action.setDisabled(True)
        self.start_action.setEnabled(True)
        self.Filter.setDisabled(False)
        self.FilterButton.setDisabled(False)
        self.choose_nicbox.setDisabled(False)
        self.timer.stop()

    """
       重新开始键响应事件
    """

    def on_actionRestart_clicked(self):
        # 重新开始清空面板内容
        self.timer.stop()
        self.core.restart_capture(self.get_choose_nic(), self.Filter.currentText())
        self.info_tree.clear()
        self.treeWidget.clear()
        self.set_hex_text("")
        """
           点击开始后，过滤器不可编辑，开始按钮，网卡选择框全部设为不可选
           激活暂停、停止键、重新开始键
        """
        self.actionRestart.setDisabled(False)
        self.start_action.setDisabled(True)
        self.Filter.setEnabled(False)
        self.FilterButton.setEnabled(False)
        self.choose_nicbox.setEnabled(False)
        self.pause_action.setEnabled(True)
        self.stop_action.setEnabled(True)
        self.timer.start(flush_time)

    """
        IP地址类型统计图绘制
    """

    def on_IP_statistics_clicked(self):
        IP = self.core.get_network_count()
        IPv4_count = IP["ipv4"]
        IPv6_count = IP["ipv6"]
        IP_count = IPv4_count + IPv6_count
        if IP_count == 0:
            reply = QMessageBox.information(self, "提示", "你还没有抓包！",
                                            QMessageBox.Cancel)

        else:
            IPv4_fre = IPv4_count / IP_count
            IPv6_fre = IPv6_count / IP_count
            data = {
                'IPv4': (IPv4_fre, '#7199cf'),
                'IPv6': (IPv6_fre, '#4fc4aa'),
            }

            fig = plt.figure(figsize=(6, 4))

            # 创建绘图区域
            ax1 = fig.add_subplot(111)
            ax1.set_title('IPv4 & IPv6 Statistical Chart')

            # 生成x轴的每个元素的位置，列表是[1,2,3,4]
            xticks = np.arange(1, 3)

            # 自定义柱状图的每个柱的宽度
            bar_width = 0.6

            IP_type = data.keys()
            values = [x[0] for x in data.values()]
            colors = [x[1] for x in data.values()]

            # 画柱状图，设置柱的边缘为透明
            bars = ax1.bar(xticks, values, width=bar_width, edgecolor='none')

            # 设置y轴的标签
            ax1.set_ylabel('Proportion')

            ax1.set_xticks(xticks)
            ax1.set_xticklabels(IP_type)

            # 设置x,y轴的范围
            ax1.set_xlim([0, 3.5])
            ax1.set_ylim([0, 1])

            # 给每一个bar分配颜色
            for bar, color in zip(bars, colors):
                bar.set_color(color)
            plt.show()

    """
        报文类型数量统计
    """

    def on_message_statistics_clicked(self):
        trans = self.core.get_transport_count()

        TCP_count = trans["tcp"]
        UDP_count = trans["udp"]
        ARP_count = trans["arp"]
        ICMP_count = trans["icmp"]

        if TCP_count + UDP_count + ARP_count + ICMP_count == 0:
            reply = QMessageBox.information(self, "提示", "你还没有抓包！",
                                            QMessageBox.Cancel)

        else:

            labels = 'TCP', 'ICMP', 'UDP', 'ARP'
            fracs = [TCP_count, ICMP_count, UDP_count, ARP_count]
            explode = [0.1, 0.1, 0.1, 0.1]  # 0.1 凸出这部分，
            plt.axes(
                aspect=1
            )  # set this , Figure is round, otherwise it is an ellipse
            # autopct ，show percet
            plt.pie(
                x=fracs,
                labels=labels,
                explode=explode,
                autopct='%3.1f %%',
                shadow=True,
                labeldistance=1.1,
                startangle=90,
                pctdistance=0.6)
            plt.show()

    """
        打开文件事件
    """

    def on_action_openfile_clicked(self):
        if self.core.start_flag or self.core.pause_flag:
            QMessageBox.warning(self, "警告", "请停止当前抓包！")
            return
        self.core.open_pcap_file()

    """
       保存文件点击事件
    """

    def on_action_savefile_clicked(self):
        if self.core.start_flag or self.core.pause_flag:
            QMessageBox.warning(self, "警告", "请停止当前抓包！")
            return
        self.core.save_captured_to_pcap()

    """
       菜单栏追踪流键点击事件
    """

    def on_action_track_clicked(self):
        if not self.Monitor or not self.Monitor.is_alive():
            self.Monitor = Process(target=start_monitor)
            self.Monitor.start()

    ''

    about = "安全系统设计 " + "软件主要功能如下：\n" + "1. 侦听指定网卡或所有网卡，抓取流经网卡的数据包；\n" + "2. 解析捕获的数据包每层的每个字段，查看数据包的详细内容；\n" + "3. 可通过不同的需求设置了BPF过滤器，获取指定地址、端口或协议等相关条件的报文；\n" + "4. 针对应用进行流量监测，监测结果实时在流量图显示，并可设置流量预警线，当流量超过预警线时自动报警；\n" + "5. 提供了以饼状图的形式统计ARP、TCP、UDP、ICMP报文，以柱状图的形式统计IPv4、IPv6报文；\n" + "6. 可将抓取到的数据包另存为pcap文件，并能通过打开一个pcap文件对其中的数据包进行解析；\n\n"

    def on_action_about_clicked(self):
        QMessageBox.information(self, "关于", self.about)

    """
       退出点击事件
    """

    def on_action_exit_clicked(self, event):
        self.closeEvent(event)

    """
        进度加载框(没用到)
        num: 加载数据数量
    """

    def showDialog(self, num):
        progress = QProgressDialog(self)
        progress.setWindowTitle("请稍等")
        progress.setLabelText("正在加载数据...")
        progress.setCancelButtonText("取消")
        progress.setMinimumDuration(1)  #进度条加载时间
        progress.setWindowModality(Qt.WindowModal)
        progress.setRange(0, num)
        for i in range(num):
            progress.setValue(i)
            if progress.wasCanceled():
                QMessageBox.warning(self, "提示", "操作失败")
                break
        progress.setValue(num)
        QMessageBox.information(self, "提示", "操作成功")


def start():
    app = QApplication([])
    ui = Ui_MainWindow()
    ui.setupUi()
    app.exec()
