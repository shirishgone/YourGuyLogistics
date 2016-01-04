(function(){
	'use strict';
	function ngRedirectTo($window){
		return{
			restrict :'A',
			link: function(scope,element,attributes){
				element.bind('click', function(event){
					$window.location.href = attributes.ngRedirectTo;
				});
			}
		};
	}

	function typeaheadFocus(){
		return{
			require:'ngModel',
			link: function(scope, element, attr, ngModel){
				element.bind('click',function(){
					var viewValue = ngModel.$viewValue;
					if (ngModel.$viewValue == ' ') {
						ngModel.$setViewValue(null);
					}
					ngModel.$setViewValue(' ');
					ngModel.$setViewValue(viewValue || ' ');
				})
			}
		}
	}

	function addProduct(Products,Errorhandler){
		return{
			restrict: 'AE',
			scope:{
				product: "=",
				createproduct: "&",
				cancel:"&",
				errmsg:"=",
				productinprocess: "="
			},
        	templateUrl: '/static/webapp/partials/directives/addProduct.html',
        	link: function ($scope, elem, attrs) {
    			$scope.getCategory = function(){
    				Products.getCategory().finally(function(){
    					var status = Errorhandler.getStatus()
    					$scope.product_category = status.data
    				})
    			}
    			$scope.getCategory()
        	}
		}
	}

	function addCustomer(){
		return{
			restrict :'AE',
			scope:{
				customer : "=",
				areacodes: "=",
				createcustomer :"&",
				cancel:"&",
				errmsg:"=",
				custinprocess: "="
			},
			templateUrl: '/static/webapp/partials/directives/addCustomer.html',
		}
	}

	function onReadFile($parse){
		return{
			restrict: 'A',
			scope:false,
			link: function(scope, element, attrs) {
				var fn = $parse(attrs.onReadFile);

				element.on('change', function(onChangeEvent) {
					var reader = new FileReader();
					// var name = file[0].name;
					reader.onload = function(onLoadEvent) {
						var data = onLoadEvent.target.result;
						var workbook = XLSX.read(data, {type: 'binary'});
						workbook = XLSX.utils.sheet_to_json(workbook.Sheets[workbook.SheetNames[0]])
						scope.$apply(function() {
							fn(scope, {$fileContent : workbook});
						});
					};
					reader.readAsBinaryString((onChangeEvent.srcElement || onChangeEvent.target).files[0]);
				});
			}
		}
	}

	function successBox(){
		return{
			restrict :'AE',
			scope:{
				message : "=",
			},
			templateUrl: '/static/webapp/partials/directives/successMessage.html',
		}
	}

	function notificationBar($window){
		return{
			restrict :'AE',
			scope:{
				message : "=",
				noticetype: "=",
			},
			templateUrl: '/static/webapp/partials/directives/notificationBar.html',
			link : function(scope,element,attrs){
				angular.element($window).bind('scroll',function(){
					if(this.pageYOffset > 63 && $window.innerWidth > 991){
						element[0].firstChild.style.position = 'fixed';
						element[0].firstChild.style.top = '0px';
						element[0].firstChild.style.left = '230px';
					}
					else if(this.pageYOffset > 63 && $window.innerWidth > 767){
						element[0].firstChild.style.position = 'fixed';
						element[0].firstChild.style.top = '0px';
						element[0].firstChild.style.left = '80px';
					}
					else if(this.pageYOffset > 63 && $window.innerWidth < 767){
						element[0].firstChild.style.position = 'fixed';
						element[0].firstChild.style.top = '0px';
						element[0].firstChild.style.left = '0px';
					}
					else{
						element[0].firstChild.style.position = 'absolute';
						element[0].firstChild.style.top = '63px';
						element[0].firstChild.style.left = '0px';
					}
					scope.$apply();
				})
			}
		}
	}

	function topBar($window){
		return{
			restrict :'AE',
			link : function(scope,element,attrs){
				angular.element($window).bind('scroll',function(){
					if(this.pageYOffset > 63 && $window.innerWidth > 991){
						element[0].style.position = 'fixed';
						element[0].style.top = '0px';
						element[0].style.width = ($window.innerWidth-230).toString();
						// element[0].style.paddingRight = '15px';
						element[0].style.left = '230px';
					}
					else if(this.pageYOffset > 63 && $window.innerWidth > 767){
						element[0].style.position = 'fixed';
						element[0].style.width = ($window.innerWidth-80).toString();
						// element[0].style.paddingRight = '15px';
						element[0].style.top = '0px';
						element[0].style.left = '80px';
					}
					else if(this.pageYOffset > 63 && $window.innerWidth < 767){
						element[0].style.position = 'fixed';
						element[0].style.top = '0px';
						element[0].style.left = '0px';
					}
					else{
						element[0].style.position = 'absolute';
						element[0].style.width = '100%';
						element[0].style.top = '63px';
						element[0].style.left = '0px';
					}
					scope.$apply();
				})
			}
		}
	}

	function clickOutside($document){
		return {
			restrict: 'A',
			scope : {
				isVisible: '=showcontent'
			},
			link: function(scope,element,attrs){
				element.bind('click',function (event){
					scope.$apply(function(){
						scope.isVisible = !(scope.isVisible)
					});
					event.stopPropagation(); 
				});
				$document.bind('click', function(){
					scope.isVisible = false;
					scope.$apply();
				});
			}
		}
	}

	function carouselControls(){
		return {
			restrict: 'A',
			link: function (scope, element, attrs) {
				scope.goNext = function() {
					element.isolateScope().next();
				};
				scope.goPrev = function() {
					element.isolateScope().prev();
				};
			}
		};
	}

	angular.module('ygwebapp').directive('ngRedirectTo', ngRedirectTo);
	angular.module('ygwebapp').directive('typeaheadFocus',typeaheadFocus);	
	angular.module('ygwebapp').directive('addProduct',addProduct);
	angular.module('ygwebapp').directive('addCustomer',addCustomer);	
	angular.module('ygwebapp').directive('onReadFile',onReadFile);
	angular.module('ygwebapp').directive('successBox',successBox);
	angular.module('ygwebapp').directive('notificationBar',notificationBar);
	angular.module('ygwebapp').directive('topBar',topBar);
	angular.module('ygwebapp').directive('clickOutside',clickOutside);
	angular.module('ygwebapp').directive('carouselControls',carouselControls);
}());