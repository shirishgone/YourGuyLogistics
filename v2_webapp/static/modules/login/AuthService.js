(function(){
	'use strice';

	angular.module('login')
	.factory('AuthService', ['$http','constants', function ($http,constants){
		return{
			login : function(userdata) {
				return $http.post(constants.v1baseUrl+'auth/login/',userdata);
			}
		};
	}]);
})();