angular.module("LWP").controller("indexCtrl", function ($rootScope, $scope, API) {
	API.containers().then(function (data) {
		$scope.containers = data.containers;
	});
});