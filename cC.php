<?
if(!defined("B_PROLOG_INCLUDED")||B_PROLOG_INCLUDED!==true)die();
$arParams["CACHE_TIME"] = $arParams["CACHE_TIME"]? intval($arParams["CACHE_TIME"]) : 36000000;

// require_once("functions.php");

/*********************************************************
				   PREPARE DATA TO COOK
*********************************************************/

// //int
// $arParams["IBLOCK_ID"] = intval($arParams["IBLOCK_ID"]);
// $arParams["IBLOCK_ID"] = $arParams["IBLOCK_ID"]? $arParams["IBLOCK_ID"] : 0;

// //string
// $arParams["IBLOCK_TYPE"] = trim($arParams["IBLOCK_TYPE"]);
// $arParams["IBLOCK_TYPE"] = strlen($arParams["IBLOCK_TYPE"])? $arParams["IBLOCK_TYPE"] : "main";

// //array
// $arParams["SOME_ARRAY"] = (is_array($arParams["SOME_ARRAY"])
// 	&& !empty($arParams["SOME_ARRAY"]))? $arParams["SOME_ARRAY"] : array();

/*********************************************************
					 MAKING DINNER
*********************************************************/

if ($this->StartResultCache()){
	$arResult = array();
	
	// if(!\Bitrix\Main\Loader::IncludeModule("iblock")){
	// 	$this->AbortResultCache();
	// 	ShowError("Модуль инфоблоков не установлен");
	// 	return;
	// }

	$this->IncludeComponentTemplate();
	// $this->EndResultCache();
}

/*********************************************************
				  LEAVE SOME BREADCRUMBS
*********************************************************/
?>