(function(){
	'use strict';
	var ydExcelDownload = function(){
		// Runs during compile
		return {
			// name: '',
			// priority: 1,
			// terminal: true,
			// controller: function($scope, $element, $attrs, $transclude) {},
			// require: 'ngModel', // Array = multiple requires, ? = optional, ^ = check parent elements
			
			// template: '',
			// templateUrl: '',
			// replace: true,
			// transclude: true,
			// compile: function(tElement, tAttrs, function transclude(function(scope, cloneLinkingFn){ return function linking(scope, elm, attrs){}})),
			scope: {
				workbookData : '=',

			}, // {} = isolate, true = child, false/undefined = no change
			restrict: 'AE', // E = Element, A = Attribute, C = Class, M = Comment
			link: function($scope, iElm, iAttrs, controller) {
				// alasql.fn.toUpperCasse = function(name){
				// 	name = name.toUpperCasse();
				// 	name = name.replace(/[^a-zA-Z0-9]/g,' ');
				// };
				var download = function(){
					alasql('SELECT * INTO XLSX("orders.xlsx",{headers:true}) FROM ?',[$scope.workbookData]);
				};
				iElm.bind('click',download);
			}
		};
	};
	angular.module('ygVendorApp')
	.directive('ydExcelDownload', 
		ydExcelDownload
	);

})();