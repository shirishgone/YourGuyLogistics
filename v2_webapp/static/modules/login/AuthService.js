(function(){
	'use strice';
	var AuthService = function ($http,constants){
		return{
			login : function(userdata) {
				return $http.post(constants.v3baseUrl+'login/',userdata);
			}
		};
	};
	
	angular.module('login')
	.factory('AuthService', [
		'$http',
		'constants', 
		AuthService
	]);
})();