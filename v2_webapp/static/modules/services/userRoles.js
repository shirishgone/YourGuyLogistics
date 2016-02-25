(function(){
	'use strice';

	var role = function ($base64,$localStorage){
		var role = {
			userrole : 'anonymous',
			authenticated : false,
			$resetUserRole : function(){
				$localStorage.$reset();
				userrole = 'anonymous';
				authenticated = false;
				return {
					userrole : userrole,
					is_authenticated : authenticated
				};
			},
			$setUserRole : function(role){
				if(role){
					userrole = role;
					authenticated = true;
				}
				else{
					userrole = 'anonymous';
					authenticated = false;
				}
			},
			$getUserRole : function(){
				return {
					userrole : userrole,
					is_authenticated : authenticated
				};
			}
		};
		return role;
	};

	angular.module('ygVendorApp')
	.factory('role', [
		'$base64',
		'$localStorage',
		role
	]);
})();