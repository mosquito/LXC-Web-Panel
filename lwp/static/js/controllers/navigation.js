angular.module("LWP").controller("navigationCtrl", function ($rootScope, $scope, $location, $interval, API) {
	$scope.actionList = [
		{icon: 'glyphicon-play', state: 'running', action: 'start', btn: 'btn-success'},
		{icon: 'glyphicon-pause', state: 'frozen', action: 'freeze', btn: 'btn-warning'},
		{icon: 'glyphicon-stop', state: 'stopped', action: 'stop', btn: 'btn-danger'}
	];

	$rootScope.selected = null;

	$scope.select = function (container) {
		$rootScope.selected = container.name;
		$location.path("/container/" + container.name);
	};

	$scope.action = function (container, action) {
		API.containerAction(container.name, action).then(update);
	};

	function update() {
		API.containers().then(function (data) {
			$rootScope.containers = data;
		});
	}

	var updateInterval = $interval(update, 10000);

	$scope.$on('$destroy',function(){
		$interval.cancel(updateInterval);
	});

	update();
});