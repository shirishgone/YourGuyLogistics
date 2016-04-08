(function(){
	'use strict';
	angular.module('notification')
	.filter('fromNow', function(){
		return function (date) {
			return moment(date).fromNow();
		};
	});

})();