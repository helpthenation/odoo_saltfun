  var loadChildren = function(node, level) {

	  
	  node = {id: "01", title: "Node", has_children: true, level: 1, children:[
		  
	  
		       {id:"011",title:'test1', has_children:true,level:2,children:[
		    	   
		       
			   {id:"012",title:'test12', has_children:false,level:3,children:[]}
			   
			   ]},
		   
		   
		   {id:"012",title:'test2', has_children:true,level:2,children:[
			   
			   
			   {id:"012",title:'test21', has_children:false,level:3,children:[]}
			   
			   
			   ]}
		   
		   ]};
   
 return node;
 };