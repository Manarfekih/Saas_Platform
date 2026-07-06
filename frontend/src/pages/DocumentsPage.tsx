import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import api from "../api/auth";
import { useAuth } from "../context/AuthContext";



type DocumentType = {

  id:number;
  filename:string;
  status:string;
  doc_type:string|null;
  extracted_text:string|null;
  error_message:string|null;

};




export default function DocumentsPage(){


const { token } = useAuth();



const [documents,setDocuments] =
useState<DocumentType[]>([]);


const [loading,setLoading] =
useState(true);


const [search,setSearch] =
useState("");






async function loadDocuments(){


if(!token)
return;


try{


const res =
await api.get(
"/documents/",
{

headers:{
Authorization:
`Bearer ${token}`
}

}
);



setDocuments(res.data);



}
catch(error){

console.error(error);

}

finally{

setLoading(false);

}


}






useEffect(()=>{


loadDocuments();


},[token]);







async function deleteDocument(id:number){



const confirm =
window.confirm(
"Are you sure you want to delete this document?"
);



if(!confirm)
return;



try{


await api.delete(

`/documents/${id}`,

{

headers:{
Authorization:
`Bearer ${token}`
}

}

);



setDocuments(prev=>
prev.filter(
doc=>doc.id!==id
)
);



}
catch(error){

console.error(error);

}



}







const filteredDocuments =

documents.filter(doc=>

doc.filename
.toLowerCase()
.includes(
search.toLowerCase()
)

);









function StatusBadge(
status:string
){



switch(status){


case "processed":

return (

<span className="
px-3 py-1
rounded-full
text-xs
font-semibold
bg-emerald-50
text-emerald-700
">

Ready

</span>

);



case "failed":

return (

<span className="
px-3 py-1
rounded-full
text-xs
font-semibold
bg-rose-50
text-rose-700
">

Failed

</span>

);



default:

return (

<span className="
px-3 py-1
rounded-full
text-xs
font-semibold
bg-amber-50
text-amber-700
animate-pulse
">

Processing

</span>

);



}



}








return (


<div className="
max-w-7xl
mx-auto
space-y-8
">





{/* Header */}


<div>


<h1 className="
text-3xl
font-bold
text-slate-900
">

Documents

</h1>



<p className="
text-slate-500
mt-2
">

Manage your AI processed documents.

</p>



</div>







{/* Search */}


<input


value={search}


onChange={
e=>setSearch(e.target.value)
}


placeholder="
Search documents...
"


className="
w-full
md:w-96
px-4
py-3
rounded-xl
border
border-slate-200
outline-none
focus:ring-2
focus:ring-indigo-500

"


/>









{/* Documents */}



<div className="
bg-white
rounded-2xl
border
border-slate-200
shadow-sm
overflow-hidden
">





{

loading ? (


<div className="
p-8
space-y-4
">


{
[1,2,3].map(i=>(

<div

key={i}

className="
h-16
rounded-xl
bg-slate-100
animate-pulse
"

/>

))

}



</div>



)

:



filteredDocuments.length===0 ?



(


<div className="
p-12
text-center
">


<h3 className="
font-semibold
text-slate-700
">

No documents

</h3>



<p className="
text-sm
text-slate-400
mt-2
">

Upload a document to start.

</p>



<Link

to="/upload"

className="
inline-block
mt-5
bg-indigo-600
text-white
px-5
py-2
rounded-lg
text-sm
font-semibold
"

>

Upload

</Link>



</div>


)

:



(



<div className="
divide-y
divide-slate-100
">


{

filteredDocuments.map(doc=>(



<div

key={doc.id}

className="
flex
justify-between
items-center
px-6
py-5
hover:bg-slate-50
transition

"


>




<div>


<Link

to={`/documents/${doc.id}`}

className="
font-semibold
text-slate-800
hover:text-indigo-600
"

>

{doc.filename}

</Link>



<div className="
flex
gap-3
items-center
mt-2
">


<span className="
text-xs
text-slate-400
">

{doc.doc_type || "Document"}

</span>



{
StatusBadge(doc.status)
}



</div>



</div>







<div className="
flex
gap-5
items-center
">


<Link

to={`/documents/${doc.id}`}

className="
text-indigo-600
text-sm
font-semibold
"

>

View

</Link>





<button

onClick={()=>
deleteDocument(doc.id)
}


className="
text-rose-600
text-sm
font-semibold
"

>

Delete

</button>



</div>





</div>



))


}



</div>



)

}



</div>





</div>


);


}