//The Anno-J configuration object
AnnoJ.config = {
    
        //List of configurations for all tracks in the Anno-J instance
        tracks : [
    
            //Example config for a ModelsTrack
            {
                id   : 'models',
                name : 'Gene Models',
                type : 'ModelsTrack',
                path : 'Annotation models',

                //Pointing to a local service
                data : '/bed/brachy',
                height : 180,
                showControls : true
            },
            // http://www.annoj.org/instances/configure.shtml
            
        ],
        
        //A list of tracks that will be active by default (use the ID of the track)
        active : [
            'models'
        ],
        
        //Address of service that provides information about this genome
        //genome    : '/proxy/arabidopsis_thaliana.php',
        genome    : '/bed/genome/brachy',
        
        //Address of service that stores / loads user bookmarks
        //bookmarks : '/bed/genome',
    
        //A list of stylesheets that a user can select between (optional)
        stylesheets : [
            {
                id   : 'css1',
                name : 'Plugins CSS',
                href : 'http://www.annoj.org/css/plugins.css',
                active : true
            },{
                id   : 'css2',
                name : 'SALK CSS',
                href : 'http://www.annoj.org/css/salk.css',
                active : true
            }       
        ],
        
        //The default 'view'. In this example, chr1, position 1, zoom ratio 20:1.
        location : {
            assembly : 'Bd1',
            position : 1,
            bases    : 80,
            pixels   : 1
        },
        
        //Site administrator contact details (optional)
        admin : {
            name  : 'Ju',
            email : 'to',
            notes : 'Pe'
        }
};
