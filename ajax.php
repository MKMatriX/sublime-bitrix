<?
/*
Принимает в виде
md5 sessid
int id
string action
array parametrs
// важно помнить что иногда необходимо подключить какой-нибудь модуль
*/
define("NO_KEEP_STATISTIC", true);
define("NOT_CHECK_PERMISSIONS", true);
require($_SERVER["DOCUMENT_ROOT"]."/bitrix/modules/main/include/prolog_before.php");
$arErrors = array();
$id = $_REQUEST["id"];
$arResult = array();
$status = "Failed";
$arParams = $_REQUEST["parametrs"];

$arPossibleErrors = Array(
	"-666" => array("Message" => "А шут его знает что не так!"),
	"-1" => array("Message" => "Нет разрешения на подобную операцию у вас"),
	"-2" => array("Message" => "Действие такое не существует"),
	"-6" => array("Message" => "Модуль инфоблоков не подключен"),
);

$ajaxError = function($error='-666') use($arErrors, $arPossibleErrors){
	$thisError = $arPossibleErrors[(String)$error];
	$thisError["CODE"] = $error;
	$arErrors[] = $thisError;
}
function no_errors() {
	global $arErrors;
	return count($arErrors) === 0;
}

// if (!\Bitrix\Main\Loader::includeModule('iblock')) {
// 	error("-6");
// }

if (check_bitrix_sessid() && $USER->IsAuthorized()){
	$arParams["USER_ID"] = $USER->GetID();
	switch ($_REQUEST["action"]) {
		
		case 'add':
			#CODE
			break;
		case 'delete':
			#CODE
			break;
		
		default:
			error("-2");
			break;
	}
} else {
	error("-1");
}

if (no_errors() && $status=="Failed") $status="Possible ok"; // такой предположительный Ок

$return = Array(
	"id"     => $id,
	"Status" => $status,
	"Errors" => $arErrors,
	"Result" => $arResult,
	// "parametrs" => $arParams,
);
die(json_encode($return));
?>