angular.module("LWP").controller("containerCtrl", function ($rootScope, $scope, $routeParams, API) {
	$scope.name = $routeParams.name;
	$rootScope.selected = $scope.name;
	API.containerInfo($scope.name).then(function (data) {
		$scope.info = data
	});
});