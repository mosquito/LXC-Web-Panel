APP = angular.module("LWP", [
	"ngRoute",
	"ngSanitize",
	"storage",
	"ui.bootstrap",
	"ui.select2"
]).config(function ($locationProvider, $httpProvider, $routeProvider) {
	delete $httpProvider.defaults.headers.common["X-Requested-With"];
	$httpProvider.defaults.withCredentials = true;
	$httpProvider.defaults.useXDomain = true;

	$routeProvider
		 .when('/', {templateUrl: '/static/partial/index.html', controller: 'indexCtrl'}
		).when('/login', {templateUrl: '/static/partial/login.html', controller: 'loginCtrl'}
	).otherwise({redirectTo: '/'});

}).run(function ($rootScope) {
	$rootScope.loader = {
		toBool: function() {
			var a=!0,b;for(b in this)"boolean"===typeof this[b]&&(a=a&&this[b]);
			a&&angular.forEach(this,function(a,b){delete this[b]});return a
		}
	};
}).directive('ngEnter', function() {
	return function(b,d,e){d.bind("keydown keypress",function(c){13===c.which&&(b.$apply(function(){b.$eval(e.ngEnter)}),c.preventDefault())})};
});