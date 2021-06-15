<?
use Bitrix\Main\Engine\ActionFilter\Authentication;
use Bitrix\Main\Engine\ActionFilter\Csrf;
use Bitrix\Main\Engine\Contract\Controllerable;
use Bitrix\Main\Loader;

class /*ComponentClassName*/ extends CBitrixComponent /*implements Controllerable*/ {
	public function onPrepareComponentParams($arParams)
	{
		$arParams["CACHE_TIME"] = $arParams["CACHE_TIME"]? intval($arParams["CACHE_TIME"]) : 36000000;
		return $arParams;
	}


	public function executeComponent() {
		$this->arResult = [];

		if ($this->StartResultCache()){

			// if(!\Bitrix\Main\Loader::IncludeModule("iblock")){
			// 	$this->AbortResultCache();
			// 	ShowError("Модуль инфоблоков не установлен");
			// 	return;
			// }

			$this->IncludeComponentTemplate();
			// $this->EndResultCache();
		}
	}


	// /**
	//  * ajax/fetch configurantion
	//  * @return array
	//  */
	// public function configureActions(): array {
	// 	return [
	// 		'ajaxMethodInThisClass' => [
	// 			'prefilters' => [
	// 				new Csrf(),
	// 				new Authentication(),
	// 			],
	// 		],
	// 	];
	// }

	// public function ajaxMethodInThisClassAction(int $id, bool $checked) {
	// }
}