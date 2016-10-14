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
def parseWord(self):
	for region in self.view.sel():
		selected = region;
		while not re.match('[\."\'\s]',self.view.substr(sublime.Region(selected.a-1,selected.a))):
			selected = sublime.Region(selected.a-1,selected.b);
			if selected.a < 5 :
				break;

		while not re.match('[\."\'\s]',self.view.substr(sublime.Region(selected.b,selected.b+1))):
			selected = sublime.Region(selected.a,selected.b+1);
			if selected.b > 20000 :
				break;

		# answer formilising
		data = {"class": self.view.substr(selected)}
		return data;

#	lists
class BitrixComponentsListCommand(sublime_plugin.WindowCommand):
	def getPathList(self):
		window = sublime.active_window();
		curFolder = window.folders()[0];
		componentsFolder = os.path.join(curFolder,"bitrix","components");
		pathList = [];
		namespacesList = os.listdir(componentsFolder);
		for namespace in namespacesList:
			if (namespace == "bitrix"): pass
			curDir = os.path.join(componentsFolder,namespace);
			if os.path.isdir(curDir):
				pathList += map(lambda x: namespace+":"+x, os.listdir(curDir));
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
		tmp = os.path.join(*item);
		path = os.path.join(curFolder,"bitrix","components",tmp,"component.php");
		window.open_file(path)
class BitrixTemplatesListCommand(sublime_plugin.WindowCommand):
	def getPathList(self):
		window = sublime.active_window();
		curFolder = window.folders()[0];
		componentsFolder = os.path.join(curFolder,"bitrix","components");
		componentsFolder2 = os.path.join(curFolder,"bitrix","templates","main","components");
		componentsFolder3 = os.path.join(curFolder,"bitrix","templates",".default","components");

		pathList = [];

		# remove all components w/o template.php
		def filterComplex(curSubDir):
			tmp = os.listdir(curSubDir);
			if os.path.isdir(curSubDir):
				tmp = filter(lambda x: os.path.isdir(os.path.join(curSubDir,x)), tmp);
				tmp = filter(lambda x: os.path.isfile(os.path.join(curSubDir,x,"template.php")), tmp);
			return tmp;

		if os.path.exists(componentsFolder):
			namespacesList = os.listdir(componentsFolder);
			for namespace in namespacesList:
				curDir = os.path.join(componentsFolder,namespace);
				if os.path.isdir(curDir):
					cList = os.listdir(curDir);
					for cName in cList:
						curSubDir = os.path.join(curDir,cName,"templates");
						tmplList = filterComplex(curSubDir);
						pathList += map(lambda x: namespace+":"+cName+":"+x, tmplList);

		if os.path.exists(componentsFolder2):
			namespacesList = os.listdir(componentsFolder2);
			for namespace in namespacesList:
				curDir = os.path.join(componentsFolder2,namespace);
				if os.path.isdir(curDir):
					cList = os.listdir(curDir);
					for cName in cList:
						curSubDir = os.path.join(curDir,cName);
						tmplList = filterComplex(curSubDir);
						pathList += map(lambda x: "main:"+namespace+":"+cName+":"+x, tmplList);

		if os.path.exists(componentsFolder3):
			namespacesList = os.listdir(componentsFolder3);
			for namespace in namespacesList:
				curDir = os.path.join(componentsFolder3,namespace);
				if os.path.isdir(curDir):
					cList = os.listdir(curDir);
					for cName in cList:
						curSubDir = os.path.join(curDir,cName);
						tmplList = filterComplex(curSubDir);
						pathList += map(lambda x: "default:"+namespace+":"+cName+":"+x, tmplList);

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
				'main': os.path.join("bitrix","templates","main","components"),
				'default' : os.path.join("bitrix","templates",".default","components"),
			}.get(x, os.path.join("bitrix","components"))
		if len(item)==3:
			item.append(item[2]);
			item[2] = "templates";
			item.insert(0,sw(item[0]));
		else:
			item[0] = sw(item[0]);
		tmp = os.path.join(*item);
		path = os.path.join(curFolder,tmp,"template.php");
		# print(path);
		window.open_file(path)
class BitrixAjaxListCommand(sublime_plugin.WindowCommand):
	def getPathList(self):
		window = sublime.active_window();
		curFolder = window.folders()[0];
		ajaxFolder = os.path.join(curFolder,"ajax");
		ajaxFolder2 = os.path.join(curFolder,"ajaxtools");

		pathList = [];
		if os.path.exists(ajaxFolder):
			pathList += map(lambda x: os.path.join("ajax",x), os.listdir(ajaxFolder));

		if os.path.exists(ajaxFolder2):
			pathList += map(lambda x: os.path.join("ajaxtools",x), os.listdir(ajaxFolder2));

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
		item = self.getPathList()[index];
		openFile(item);
class BitrixPagesListCommand(sublime_plugin.WindowCommand):
	def getPathList(self):
		window = sublime.active_window();
		curFolder = window.folders()[0];

		pathList = [];
		if os.path.exists(curFolder):
			pathList += map(lambda x: x, os.listdir(curFolder));
			pathList = list(filter(lambda x: '.' not in x, pathList)); # remove .git and ect
			ignore = ['bitrix','upload','html','desktop_app'];
			pathList = list(filter(lambda x: x not in ignore, pathList));

			pathList = list(filter(lambda x: os.path.isfile(
				os.path.join(curFolder,x,"index.php")) , pathList));

		return sorted(pathList);
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
		item = os.path.join(self.getPathList()[index],"index.php");
		openFile(item);
class BitrixHtmlListCommand(sublime_plugin.WindowCommand):
	def getPathList(self):
		window = sublime.active_window();
		curFolder = window.folders()[0];
		html = os.path.join(curFolder, "html");

		pathList = [];
		if os.path.exists(html):
			for root, dirs, files in os.walk(html, topdown=False):
				relativeRoot = root.replace(html,'',1)[1:];
				for name in files:
					if re.match(".*\.php",name):
						pathList += [os.path.join(relativeRoot,name)];

		return sorted(pathList);
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
		item = os.path.join("html",self.getPathList()[index]);
		openFile(item);

#	in text open
class BitrixPhpOpenCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		window = sublime.active_window()
		curFolder = window.folders()[0]
		data = parsePhpInclude(self)

		if data['file'][0] == "/":
			print("TODO: absolute path by php")
			# filePath = curFolder + data["file"]
		else:
			filePath = os.path.join(window.extract_variables()["file_path"],data['file']);
			window.open_file(filePath)
		# print(filePath)
class BitrixAjaxOpenCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		window = sublime.active_window()
		curFolder = window.folders()[0]
		data = parseAjax(self)

		if data['url'][0] == "/":
			filePath = os.path.join(curFolder, data['url']);

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

		componentPath = os.path.join(curFolder,'bitrix','components',data['namespace'],data['component']);
		componentFile = os.path.join(componentPath,"component.php");
		# print(componentFile)
		window.open_file(componentFile)
class BitrixGetComponentTemplatePathCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		window = sublime.active_window()
		curFolder = window.folders()[0]
		data = parseInclude(self)

		componentPath = os.path.join(curFolder,'bitrix','components',data['namespace'],data['component']);
		templatePath = os.path.join(componentPath,"templates");
		templateFile = os.path.join(templatePath,data['template'],"template.php");
		# print(templateFile)
		window.open_file(templateFile)

# create new component
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

# utils
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
	window = sublime.active_window();
	curFolder = window.folders()[0];
	if path[0] == '/':
		path = path[1:];
	path = os.path.join(curFolder,path);
	window.open_file(path);

#	open const files
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

#	in component menu
class BitrixTemplateMenuCommand(sublime_plugin.WindowCommand):
	def getPathList(self):
		window = sublime.active_window();
		curFolder = window.folders()[0];
		view = window.active_view();
		file = view.file_name();
		templateFolder = os.path.dirname(file);
		# print(os.path.basename(os.path.dirname(templateFolder)));
		if os.path.basename(os.path.dirname(templateFolder)) != "templates":
			return [];

		pathList = [];
		files = filter(lambda x: x == os.path.isfile(os.path.join(templateFolder,x)), os.listdir(templateFolder));
		pathList += filter(lambda x: x != os.path.basename(file), files);
		componentPath = os.path.dirname(os.path.dirname(templateFolder));
		componentPath = os.path.join(componentPath,'component.php');
		print(componentPath);
		if os.path.exists(componentPath):
			pathList += ['../../component.php'];

		if "template.php" in os.listdir(templateFolder):
			if "component_epilog.php" not in os.listdir(templateFolder):
				pathList += ["create:component_epilog.php"]
			if "result_modifier.php" not in os.listdir(templateFolder):
				pathList += ["create:result_modifier.php"]
		return pathList;
	def run(self): 
		window = sublime.active_window();
		window.show_quick_panel(self.getPathList(), self.on_chosen)
	def on_chosen(self, index):
		window = sublime.active_window();
		curFolder = window.folders()[0];
		view = window.active_view();
		file = view.file_name();
		templateFolder = os.path.dirname(file);
		if index == -1: return
		# if not isView(self.vid):
		# 	sublime.status_message('You are in a different view.')
		# 	return
		el = self.getPathList()[index];
		if "create:" not in el :
			while '../' in el :
				el = el[3:];
				templateFolder = os.path.dirname(templateFolder);
			window.open_file(os.path.join(templateFolder,el));
		else:
			el=el.split(":")[1];
			createFileFromTemplate(os.path.join(templateFolder,el), 't'+el[0].upper()+'.php', '');
			window.open_file(os.path.join(templateFolder,el));
class BitrixComponentMenuCommand(sublime_plugin.WindowCommand):
	def getPathList(self):
		window = sublime.active_window();
		curFolder = window.folders()[0];
		view = window.active_view();
		file = view.file_name();
		templateFolder = os.path.join(os.path.dirname(file),"templates");
		pathList = [];
		if os.path.exists(templateFolder):
			tmplList = os.listdir(templateFolder);
			for template in tmplList:
				curDir = os.path.join(templateFolder,template);
				fList = filter(lambda x: os.path.isfile(os.path.join(curDir,x)), os.listdir(curDir));
				pathList += map(lambda x: "templates/"+template+"/"+x, fList);
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
		curFolder = os.path.dirname(file);
		if index == -1: return
		# if not isView(self.vid):
		# 	sublime.status_message('You are in a different view.')
		# 	return
		el = self.getPathList()[index];
		if "create:" not in el :
			while '../' in el :
				el = el[3:];
				templateFolder = os.path.dirname(templateFolder);
			# pprint(curFolder +el);
			window.open_file(os.path.join(curFolder,el));
		else:
			el=el.split(":")[1];
			createFileFromTemplate(os.path.join(templateFolder,el), 't'+el[0].upper()+'.php', '');
			window.open_file(os.path.join(templateFolder,el));

# already not needed
class BitrixOpenClassCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		window = sublime.active_window()
		curFolder = window.folders()[0]
		data = parseWord(self)
		# print(data)
		# window.open_file(filePath)
		openFile('/bitrix/templates/main/template_styles.css');
		search = '\.'+data['class']+'[\s]*[{]([^}]*)[}]';
		fResult = window.active_view().find(search,0);
		window.active_view().show_at_center(fResult);