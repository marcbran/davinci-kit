local d = import '../main.libsonnet';

// This function will provide a MediaIn tool to the function for further connections
// The returned tool will then be connected to a MediaOut tool
d.MediaInOut(function(mediaIn) mediaIn)
