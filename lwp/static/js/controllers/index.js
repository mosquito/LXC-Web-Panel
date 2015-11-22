angular.module("LWP").controller("indexCtrl", function ($rootScope, $scope, $interval, API) {
	$scope.labelClass = function (key) {
		return ({
			stopped: 'label-danger',
			frozen: 'label-warning',
			running: 'label-success'
		})[key];
	};
});