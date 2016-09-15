<? if(!defined("B_PROLOG_INCLUDED")||B_PROLOG_INCLUDED!==true)die();

//component_epilog
$arResult["CACHED_TPL"] = preg_replace_callback(
  "/#RATING_([\d]+)#/is".BX_UTF_PCRE_MODIFIER,
    function ($matches){
        ob_start();
        global $APPLICATION;
        $APPLICATION->IncludeComponent(
           "alfateam:rating.detail", "",
            array("RATING" => getRatingByID($matches[1]),true)
        );
        $retrunStr = @ob_get_contents();
        ob_get_clean();
        return $retrunStr;
    },
  $arResult["CACHED_TPL"]
);

echo $arResult["CACHED_TPL"];
?>
