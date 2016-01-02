(function(){
	'use strice';

	var role = function ($base64,$localStorageProvider){
		var userrole ;
		return {
			setUserRole: function (){
				var x = $base64.decode($localStorageProvider.get('token'));
				userrole = x;
			},
			$get : function(){
				return {
					userrole: userrole
				};
			}

		};
	};

	angular.module('ygVendorApp')
	.provider('role', [
		'$base64',
		'$localStorageProvider',
		role
	]);
})();