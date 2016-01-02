(function(){
	'use strict';
	var LoginCntrl = function ($state,AuthService,UserData,$localStorage,role){
		this.userLogin = function(){
			var data = {
				username : this.username,
				password : this.password
			};
			AuthService.login(data).then(function (response){
				console.log(response.data);
				$localStorage.$reset();
				$localStorage.token = response.data.auth_token;
				console.log(role.userrole);
			});
		};
	};

	angular.module('login', [])
	.config(['$stateProvider',function ($stateProvider) {
		$stateProvider
		.state('login', {
			url : '/login',
			templateUrl : '/static/modules/login/login.html',
			controllerAs : 'login',
			controller: 'LoginCntrl'
		});
	}])
	.controller('LoginCntrl', [
		'$state', 
		'AuthService',
		'UserData',
		'$localStorage',
		'role',
		LoginCntrl
	]);
})();