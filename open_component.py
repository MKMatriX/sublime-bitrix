import sublime, sublime_plugin, re
import os
import string

from pprint import pprint


def initial():
	# rootFolder = [sublime.active_window().folders()[0]]; #root folder
	global rootFolder
	global compenentsPaths
	global templatesPaths
	global complexTemplatesPaths
	global ajaxPaths
	global compenentsList
	global templatesList
	global ajaxList
	global complexTemplatesList
	global window

	window = sublime.active_window()
	rootFolder = sublime.active_window().folders(); #root folder
	compenentsPaths = [
		["bitrix", "components","$namespace", "$component", "$|file|component.php|class.php"],
		["local", "components","$namespace", "$component", "$|file|component.php|class.php"]
	];
	templatesPaths = [
		["bitrix", "templates","$siteTemplate", "components", "$namespace", "$component", "$template", "template.php"],
		["bitrix", "components","$namespace", "$component", "templates", "$template", "template.php"],
		["local", "templates","$siteTemplate", "components", "$namespace", "$component", "$template", "template.php"],
		["local", "components","$namespace", "$component", "templates", "$template", "template.php"]
	];
	complexTemplatesPaths = [
		["bitrix", "components","$namespace", "$component", "templates", "$template", "$name"],
		["bitrix", "templates","$siteTemplate", "components", "$namespace", "$component", "$template", "$name"],
		["local", "components","$namespace", "$component", "templates", "$template", "$name"],
		["local", "templates","$siteTemplate", "components", "$namespace", "$component", "$template", "$name"]
	];
	ajaxPaths = [
		["ajax", "$name"],
		["ajaxtools", "$name"]
	]

	#initial (can be skipped, or left the only one)
	# compenentsList = [];
	# templatesList = [];
	# ajaxList = [];
	# complexTemplatesList = [];

def pathsToPaths(ar):
	initial()
	paths = []
	for sar in ar:
		paths += arrayToPath(sar)
	# pprint(paths)
	# paths = filter(lambda x: os.path.isfile(x["path"]), paths);
	return paths

def arrayToPath(ar):
	paths = []
	rootFolder = sublime.active_window().folders(); #root folder

	for root in rootFolder:
		paths.append({"path": root})
	opath = paths[0];
	for folder in ar:
		nextpaths = [];
		for opath in paths:
			path = opath["path"]
			if ("$|" == folder[:2]):
				split = folder.split('|')
				propname = split[1]
				pathVariants = split[2:]
				for subpath in pathVariants:
					osubpath = opath.copy()
					osubpath[propname] = subpath
					osubpath["path"] = os.path.join(path, subpath)
					nextpaths.append(osubpath)
				else:
					print("not a folder " + path);
					pass
			elif ("$" == folder[0]):
				propname = folder[1:]
				if os.path.isdir(path):
					for subpath in os.listdir(path):
						osubpath = opath.copy()
						osubpath[propname] = subpath
						osubpath["path"] = os.path.join(path, subpath)
						nextpaths.append(osubpath)
				else:
					print("not a folder " + path);
					pass
			else:
				opath["path"] = os.path.join(path, folder)
				nextpaths.append(opath)
		paths = nextpaths
	return paths;

rootFolder = sublime.active_window().folders(); #root folder
compenentsPaths = [
	["bitrix", "components","$namespace", "$component", "$|file|component.php|class.php"],
	["local", "components","$namespace", "$component", "$|file|component.php|class.php"]
];
templatesPaths = [
	["bitrix", "templates","$siteTemplate", "components", "$namespace", "$component", "$template", "template.php"],
	["bitrix", "components","$namespace", "$component", "templates", "$template", "template.php"],
	["local", "templates","$siteTemplate", "components", "$namespace", "$component", "$template", "template.php"],
	["local", "components","$namespace", "$component", "templates", "$template", "template.php"]
];
complexTemplatesPaths = [
	["bitrix", "components","$namespace", "$component", "templates", "$template", "$name"],
	["bitrix", "templates","$siteTemplate", "components", "$namespace", "$component", "$template", "$name"],
	["local", "components","$namespace", "$component", "templates", "$template", "$name"],
	["local", "templates","$siteTemplate", "components", "$namespace", "$component", "$template", "$name"]
];
ajaxPaths = [["ajax", "$name"], ["ajaxtools", "$name"]]

#initial (can be skipped, or left the only one)
# compenentsList = pathsToPaths(compenentsPaths);
# templatesList = pathsToPaths(templatesPaths);
# ajaxList = pathsToPaths(ajaxPaths);
# complexTemplatesList = [];

compenentsList = [];
templatesList = [];
ajaxList = [];
complexTemplatesList = [];


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
	def run(self):
		global compenentsList;
		compenentsList = pathsToPaths(compenentsPaths);
		compenentsList = [c for c in compenentsList if os.path.isfile(c['path'])]
		panelList = []
		panelList[:] = [c["namespace"]+":"+c["component"]+" "+c["file"] for c in compenentsList]
		window.show_quick_panel(panelList, self.on_chosen)
	def on_chosen(self, index):
		if index == -1: return
		# if not isView(self.vid):
		# 	sublime.status_message('You are in a different view.')
		# 	return
		window.open_file(compenentsList[index]["path"])
class BitrixTemplatesListCommand(sublime_plugin.WindowCommand):
	def run(self):
		global templatesList;
		templatesList = pathsToPaths(templatesPaths);
		# pprint(templatesList)
		panelList = []
		for t in templatesList:
			if "siteTemplate" in t.keys():
				niceName = t["siteTemplate"]+"/"+t["namespace"]+":"+t["component"]+":"+t["template"]
			else:
				niceName = t["namespace"]+":"+t["component"]+":"+t["template"]
			panelList.append(niceName)
		window.show_quick_panel(panelList, self.on_chosen)
	def on_chosen(self, index):
		if index == -1: return
		# if not isView(self.vid):
		# 	sublime.status_message('You are in a different view.')
		# 	return
		# pprint(templatesList)
		window.open_file(templatesList[index]["path"])
class BitrixComplexTemplatesListCommand(sublime_plugin.WindowCommand):
	def run(self):
		global complexTemplatesList, templatesList;
		nonCompex = [];
		nonCompex[:] = [t["component"] for t in templatesList if os.path.isfile(t["path"])]
		complexTemplatesList[:] = [c for c in pathsToPaths(complexTemplatesPaths) if c["component"] not in nonCompex]
		panelList = []
		for t in complexTemplatesList:
			if "siteTemplate" in t.keys():
				niceName = t["siteTemplate"]+"/"+t["namespace"]+":"
			else:
				niceName = t["namespace"]+":"
			if t["template"] == ".default":
				niceName += t["component"]
			else:
				niceName += t["component"]+":"+t["template"]
			niceName += " - " + t["name"]
			panelList.append(niceName)
		window.show_quick_panel(panelList, self.on_chosen)
	def on_chosen(self, index):
		if index == -1: return
		# if not isView(self.vid):
		# 	sublime.status_message('You are in a different view.')
		# 	return
		window.open_file(complexTemplatesList[index]["path"])
class BitrixAjaxListCommand(sublime_plugin.WindowCommand):
	def run(self):
		global ajaxList;
		ajaxList = pathsToPaths(ajaxPaths);
		panelList[:] = [c["name"] for c in ajaxList]
		window.show_quick_panel(panelList, self.on_chosen)
	def on_chosen(self, index):
		if index == -1: return
		if not isView(self.vid):
			sublime.status_message('You are in a different view.')
			return
		# pprint(ajaxList)
		window.open_file(ajaxList[index]["path"])
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

		componentPath = curFolder + '/local/components/'+data['namespace']+'/'+data['component']+"/"
		templatePath = componentPath + "templates/" + data['template'] + '/'

		# works only if no such folders
		if not os.path.exists(templatePath):
			# making folders
			os.makedirs(templatePath)

			# path relative to site dir
			cC = componentPath + "class.php"
			cP = componentPath + ".parameters.php"
			cD = componentPath + ".description.php"
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



def BitrixOpenFileFromSelectedList(index):
	if index == -1: return
	window.open_file(selectedList[index]["path"])

#	open const files
class BitrixOpenHeaderCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		global selectedList;
		selectedList = pathsToPaths([
			["$|folder|bitrix|local", "templates","$template", "header.php"],
		])
		panelList = [c["folder"]+" : "+c["template"] for c in selectedList]
		window.show_quick_panel(panelList, BitrixOpenFileFromSelectedList)
class BitrixOpenFooterCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		global selectedList;
		selectedList = pathsToPaths([
			["$|folder|bitrix|local", "templates","$template", "footer.php"],
		])
		panelList = [c["folder"]+" : "+c["template"] for c in selectedList]
		window.show_quick_panel(panelList, BitrixOpenFileFromSelectedList)
class BitrixOpenStylesheetCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		global selectedList;
		selectedList = pathsToPaths([
			["$|folder|bitrix|local", "templates","$template", "template_styles.css"],
			["$|folder|bitrix|local", "templates","$template", "css", "$|file|custom.css|style.css"],
		])
		selectedList = [c for c in selectedList if os.path.exists(c["path"])]
		panelList = []
		for c in selectedList:
			if 'file' in c:
				panelList.append(c["folder"]+" : "+c["template"]+"/css/"+c['file'])
			else:
				panelList.append(c["folder"]+" : "+c["template"]+"/template_styles.css")
		window.show_quick_panel(panelList, BitrixOpenFileFromSelectedList)
class BitrixOpenJsCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		global selectedList;
		selectedList = pathsToPaths([
			["$|folder|bitrix|local", "templates","$template", "js", "$|file|main.js|ajax.js|custom.js"],
		])
		selectedList = [c for c in selectedList if os.path.exists(c["path"])]
		panelList = [c["folder"]+" : "+c["template"]+"/js/"+c["file"] for c in selectedList]
		window.show_quick_panel(panelList, BitrixOpenFileFromSelectedList)
class BitrixOpenInitCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		global selectedList;
		selectedList = pathsToPaths([
			["$|folder|bitrix|local", "php_interface", "init.php"],
		])
		selectedList = [c for c in selectedList if os.path.exists(c["path"])]
		panelList = [c["folder"] for c in selectedList]
		if len(selectedList) == 1:
			openFile(selectedList[0]["path"])
		else:
			window.show_quick_panel(panelList, BitrixOpenFileFromSelectedList)

#	in component menu
class BitrixTemplateMenuCommand(sublime_plugin.WindowCommand):
	def getPathList(self):
		window = sublime.active_window();
		curFolder = window.folders()[0];
		view = window.active_view();
		file = view.file_name();
		templateFolder = os.path.dirname(file);
		# print(os.path.basename(os.path.dirname(templateFolder)));

		pathList = [];
		files = filter(lambda x: os.path.isfile(os.path.join(templateFolder,x)), os.listdir(templateFolder));
		pathList += filter(lambda x: x != os.path.basename(file), files);
		# pprint(pathList);
		if os.path.basename(os.path.dirname(templateFolder)) == "templates":
			componentPath = os.path.dirname(os.path.dirname(templateFolder));
			if os.path.exists(componentPath):
				componentFiles = filter(lambda x: os.path.isfile(os.path.join(componentPath,x)), os.listdir(componentPath));
				pathList += map(lambda x: '../../'+x, componentFiles);

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
		componentFolder = os.path.dirname(file);
		templateFolder = os.path.join(componentFolder,"templates");
		pathList = [];
		pathList += filter(lambda x: os.path.isfile(os.path.join(componentFolder,x)), os.listdir(componentFolder));
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
		componentFolder = os.path.dirname(file);
		templateFolder = os.path.join(componentFolder,"templates");
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