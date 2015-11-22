angular.module("LWP").controller("indexCtrl", function ($rootScope, $scope, API) {
	$scope.selected = null;

	$scope.actionList = [
		{icon: 'glyphicon-play', state: 'running', action: 'start', btn: 'btn-success'},
		{icon: 'glyphicon-pause', state: 'frozen', action: 'freeze', btn: 'btn-warning'},
		{icon: 'glyphicon-stop', state: 'stopped', action: 'stop', btn: 'btn-danger'}
	];

	$scope.labelClass = function (key) {
		return ({
			stopped: 'label-danger',
			frozen: 'label-warning',
			running: 'label-success'
		})[key];
	};

	$scope.select = function (container) {
		$scope.selected = container.name;
	};

	$scope.action = function (container, action) {
		API.containerAction(container.name, action).then(update);
	};

	function update() {
		API.containers().then(function (data) {
			$scope.containers = data;
		});
	}

	update();
});