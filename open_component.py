import sublime, sublime_plugin, re
import os
import string

from pprint import pprint

def parseInclude(self):
	for region in self.view.sel():
		line = self.view.line(region)
		lineContents = self.view.substr(line)

		# looking for that function
		while not re.match('.*\$APPLICATION.*->.*IncludeComponent.*\(.*',lineContents):
			region = sublime.Region(line.a-1,line.a-1)
			line = self.view.line(region)
			lineContents = self.view.substr(line)
			if line.a < 5 :
				break;

		# connecting until we get two first parameters
		while lineContents.count(',') != 2:
			region = sublime.Region(line.b+1,line.b+1)
			line = self.view.line(region)
			lineContents += self.view.substr(line)
			if (";" in lineContents) or ("?>" in lineContents):
				break;

		# reg to extract data
		parser = re.search ('.*IncludeComponent.*["|\'](.*):(.*)["|\'].*,.*["|\'](.*)[\'|"].*', lineContents)

		# answer formilising
		data = {"namespace": parser.group(1), "component": parser.group(2), "template": parser.group(3)}
		#  if template is empty
		# TODO: if template equals false, and if template in another folder
		if data['template'] == '':
			data['template'] = '.default'
		return data;
def parseAjax(self):
	for region in self.view.sel():
		line = self.view.line(region)
		lineContents = self.view.substr(line)

		# one line only
		while not re.match('.*\$\.ajax[\s]*\([\s]*{.*',lineContents): 
			region = sublime.Region(line.a-1,line.a-1)
			line = self.view.line(region)
			lineContents = self.view.substr(line)
			if line.a < 5 :
				break;

		# connecting until we get two first parameters
		while lineContents.count(',') != 1:
			region = sublime.Region(line.b+1,line.b+1)
			line = self.view.line(region)
			lineContents += self.view.substr(line)
			if (";" in lineContents) or ("?>" in lineContents):
				break;

		# reg to extract data
		parser = re.search ('.*url.*:.*["|\'](.*)["|\'].*,.*', lineContents)

		# answer formilising
		data = {"url": parser.group(1)}
		return data;
def parsePhpInclude(self):
	for region in self.view.sel():
		line = self.view.line(region)
		lineContents = self.view.substr(line)

		# one line only
		while not re.match('.*(require|include).*',lineContents): 
			region = sublime.Region(line.a-1,line.a-1)
			line = self.view.line(region)
			lineContents = self.view.substr(line)
			if line.a < 5 :
				break;

		# reg to extract data
		parser = re.search ('.*[requre|include].*\(.*["|\'](.*)["|\'].*\).*', lineContents)


		# answer formilising
		data = {"file": parser.group(1)}
		return data;

class BitrixComponentsListCommand(sublime_plugin.WindowCommand):
	def getPathList(self):
		window = sublime.active_window();
		curFolder = window.folders()[0];
		componentsFolder = curFolder+"/bitrix/components/";
		pathList = [];
		namespacesList = os.listdir(componentsFolder);
		for namespace in namespacesList:
			if (namespace == "bitrix"): pass
			pathList += map(lambda x: namespace+":"+x, os.listdir(componentsFolder+namespace+"/"));
		return pathList;
	def run(self): 
		window = sublime.active_window();
		curFolder = window.folders()[0];
		window.show_quick_panel(self.getPathList(), self.on_chosen)
	def on_chosen(self, index):
		window = sublime.active_window();
		curFolder = window.folders()[0];
		if index == -1: return
		# if not isView(self.vid):
		# 	sublime.status_message('You are in a different view.')
		# 	return
		path = curFolder+"/bitrix/components/"+self.getPathList()[index].replace(":","/")+"/component.php";
		window.open_file(path)
class BitrixTemplatesListCommand(sublime_plugin.WindowCommand):
	def getPathList(self):
		window = sublime.active_window();
		curFolder = window.folders()[0];
		componentsFolder = curFolder+"/bitrix/components/";
		componentsFolder2 = curFolder+"/bitrix/templates/main/components/";
		componentsFolder3 = curFolder+"/bitrix/templates/.default/components/";

		pathList = [];
		if os.path.exists(componentsFolder):
			namespacesList = os.listdir(componentsFolder);
			for namespace in namespacesList:
				curDir = componentsFolder+namespace+"/";
				cList = os.listdir(curDir);
				for cName in cList:
					curSubDir = curDir+cName+"/templates/";
					if os.path.exists(curSubDir):
						pathList += map(lambda x: namespace+":"+cName+":"+x, os.listdir(curSubDir));

		if os.path.exists(componentsFolder2):
			namespacesList = os.listdir(componentsFolder2);
			for namespace in namespacesList:
				curDir = componentsFolder2+namespace+"/";
				cList = os.listdir(curDir);
				for cName in cList:
					curSubDir = curDir+cName;
					if os.path.exists(curSubDir):
						pathList += map(lambda x: "main:"+namespace+":"+cName+":"+x, os.listdir(curSubDir));

		if os.path.exists(componentsFolder3):
			namespacesList = os.listdir(componentsFolder3);
			for namespace in namespacesList:
				curDir = componentsFolder3+namespace+"/";
				cList = os.listdir(curDir);
				for cName in cList:
					curSubDir = curDir+cName;
					if os.path.exists(curSubDir):
						pathList += map(lambda x: "default:"+namespace+":"+cName+":"+x, os.listdir(curSubDir));

		return pathList;
	def run(self): 
		window = sublime.active_window();
		curFolder = window.folders()[0];
		window.show_quick_panel(self.getPathList(), self.on_chosen)
	def on_chosen(self, index):
		window = sublime.active_window();
		curFolder = window.folders()[0];
		if index == -1: return
		# if not isView(self.vid):
		# 	sublime.status_message('You are in a different view.')
		# 	return
		item = self.getPathList()[index].split(":");
		def sw(x):
			return {
				'main': "/bitrix/templates/main/components",
				'default' : "/bitrix/templates/.default/components",
			}.get(x, "/bitrix/components")
		if len(item)==3:
			item.append(item[2]);
			item[2] = "templates";
			item.insert(0,sw(item[0]));
		else:
			item[0] = sw(item[0]);
		path = curFolder+"/".join(item)+"/template.php";
		window.open_file(path)

class BitrixPhpOpenCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		window = sublime.active_window()
		curFolder = window.folders()[0]
		data = parsePhpInclude(self)

		if data['file'][0] == "/":
			print("TODO: absolute path by php")
			# filePath = curFolder + data["file"]
		else:
			filePath = window.extract_variables()["file_path"] + "/" + data['file'];
			window.open_file(filePath)
		# print(filePath)
class BitrixAjaxOpenCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		window = sublime.active_window()
		curFolder = window.folders()[0]
		data = parseAjax(self)

		if data['url'][0] == "/":
			filePath = curFolder + data['url'];

			createFileFromTemplate(filePath, 'ajax.php', '');

			# print(filePath)
			window.open_file(filePath)
		else: 
			print("Not looking as part of site: " + data['url'])
class BitrixGetComponentPathCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		window = sublime.active_window()
		curFolder = window.folders()[0]
		data = parseInclude(self)

		componentPath = curFolder + '/bitrix/components/'+data['namespace']+'/'+data['component']+"/"
		componentFile = componentPath + "component.php";
		# print(componentFile)
		window.open_file(componentFile)
class BitrixGetComponentTemplatePathCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		window = sublime.active_window()
		curFolder = window.folders()[0]
		data = parseInclude(self)

		componentPath = curFolder + '/bitrix/components/'+data['namespace']+'/'+data['component']+"/"
				
		templatePath = componentPath + "templates/"
		templateFile = templatePath + data['template'] + "/template.php"
		# print(templateFile)
		window.open_file(templateFile)

class BitrixNewComponentCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		window = sublime.active_window()
		curFolder = window.folders()[0]
		data = parseInclude(self)

		componentPath = curFolder + '/bitrix/components/'+data['namespace']+'/'+data['component']+"/"
		templatePath = componentPath + "templates/" + data['template'] + '/'

		# works only if no such folders
		if not os.path.exists(templatePath):
			# making folders
			os.makedirs(templatePath)

			# path relative to site dir
			cC = componentPath + "component.php"
			cP = componentPath + ".parameters.php"
			cD = componentPath + ".decription.php"
			cT = templatePath  + "template.php"

			# path to site dir
			__location__ = os.path.realpath(
				os.path.join(os.getcwd(), os.path.dirname(__file__)))

			# join to get absolute paths
			eC = os.path.join(__location__, 'cC.php')
			eP = os.path.join(__location__, 'cP.php')
			eD = os.path.join(__location__, 'cD.php')
			eT = os.path.join(__location__, 'cT.php')

			# creating php files
			file = open(cC, 'a')
			file.close()
			file = open(cP, 'a')
			file.close()
			file = open(cD, 'a')
			file.close()
			file = open(cT, 'a')
			file.close()

			# filling em with templates
			with open(eC) as f:
				lines = f.readlines()
				# lines = [l for l in lines if "ROW" in l]
				with open(cC, "w") as f1:
					f1.writelines(lines)
			with open(eD) as f:
				lines = f.readlines()
				# insert code here to change #name# to smthg
				with open(cD, "w") as f1:
					f1.writelines(lines)
			with open(eP) as f:
				lines = f.readlines()
				with open(cP, "w") as f1:
					f1.writelines(lines)
			with open(eT) as f:
				lines = f.readlines()
				with open(cT, "w") as f1:
					f1.writelines(lines)

			# opening for edition
			window.open_file(cC)
			window.open_file(cT)

def createFileFromTemplate(filePath, templatePath, replaceArray):
	folder = os.path.basename(filePath);
	# if not os.path.exists(folder):
	# 	os.makedirs(folder)
	# plugin folder
	__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
	templateFile = os.path.join(__location__, templatePath)
	if not os.path.isfile(filePath):
		# create file
		file = open(filePath, 'a')
		file.close()
		# fill from template
		with open(templateFile) as f:
			lines = f.readlines()
			with open(filePath, "w") as f1:
				f1.writelines(lines)
def openFile(path):
	window = sublime.active_window()
	curFolder = window.folders()[0]
	path = curFolder + path
	window.open_file(path)

class BitrixOpenHeaderCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		openFile('/bitrix/templates/main/header.php');
class BitrixOpenFooterCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		openFile('/bitrix/templates/main/footer.php');
class BitrixOpenStylesheetCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		openFile('/bitrix/templates/main/template_styles.css');
class BitrixOpenJsCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		openFile('/bitrix/templates/main/js/main.js');
class BitrixOpenInitCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		openFile('/bitrix/php_interface/init.php');
class BitrixTemplateMenuCommand(sublime_plugin.WindowCommand):
	def getPathList(self):
		window = sublime.active_window();
		curFolder = window.folders()[0];
		view = window.active_view();
		file = view.file_name();
		templateFolder = os.path.dirname(file)+"/";
		if list(reversed(templateFolder.split('/')))[2] != "templates":
			return

		pathList = [];
		pathList += map(lambda x: x, os.listdir(templateFolder));
		componentPath = list(templateFolder.split('/'));
		del componentPath[-1];
		del componentPath[-1];
		del componentPath[-1];
		componentPath = '/'.join(componentPath)+'/component.php';
		if os.path.exists(componentPath):
			pathList += ['../../component.php'];

		if "template.php" in pathList:
			if "component_epilog.php" not in pathList:
				pathList += ["create:component_epilog.php"]
			if "result_modifier.php" not in pathList:
				pathList += ["create:result_modifier.php"]
		return pathList;
	def run(self): 
		window = sublime.active_window();
		# curFolder = window.folders()[0];
		# self.getPathList();
		window.show_quick_panel(self.getPathList(), self.on_chosen)
	def on_chosen(self, index):
		window = sublime.active_window();
		curFolder = window.folders()[0];
		view = window.active_view();
		file = view.file_name();
		templateFolder = os.path.dirname(file)+"/";
		if index == -1: return
		# if not isView(self.vid):
		# 	sublime.status_message('You are in a different view.')
		# 	return
		el = self.getPathList()[index];
		if "create:" not in el :
			while '../' in el :
				el = el[3:];
				tmp = list(templateFolder.split('/'));
				del tmp[-1];
				del tmp[-1];
				templateFolder = '/'.join(tmp)+'/';
			# pprint(templateFolder+el);
			window.open_file(templateFolder+el)
		else:
			el=el.split(":")[1];
			createFileFromTemplate(templateFolder+el, 't'+el[0].upper()+'.php', '');
			window.open_file(templateFolder+el)