import { useEffect, useState } from "react";
import { Link, useParams , useNavigate } from "react-router-dom";

import api from "../api/auth";
import { useAuth } from "../context/AuthContext";




type Document = {

  id:number;
  filename:string;
  status:string;
  doc_type:string|null;
  extracted_text:string|null;
  error_message:string|null;

};



type StatusResponse = {

  id:number;
  status:string;
  processing_step:string|null;
  progress:number;
  error_message:string|null;

};





export default function DocumentDetailsPage(){


const { id } = useParams();

const { token } = useAuth();



const [document,setDocument] =
useState<Document|null>(null);


const [status,setStatus] =
useState<StatusResponse|null>(null);


const [loading,setLoading] =
useState(true);

const navigate = useNavigate();


async function openChat() {
  if (!token || !id) return;

  try {
    const res = await api.get(
      `/documents/${id}/chat-session`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    navigate(`/chat/${id}`, {
      state: {
        session_id: res.data.session_id,
      },
    });
  } catch (error) {
    console.error(error);
  }
}



async function loadDocument(){


if(!token || !id)
return;


try{
const res =
await api.get(
`/documents/${id}`,
{
headers:{
Authorization:`Bearer ${token}`
}
}
);


setDocument(res.data);



}
catch(error){

console.error(error);

}

}





async function loadStatus(){


if(!token || !id)
return;



try{


const res =
await api.get(
`/documents/${id}/status`,
{
headers:{
Authorization:`Bearer ${token}`
}
}
);



setStatus(res.data);



}
catch(error){

console.error(error);

}


}






useEffect(()=>{


loadDocument()
.then(()=>setLoading(false));


loadStatus();



const interval =
setInterval(()=>{


loadStatus();


},3000);



return ()=>clearInterval(interval);



},[token,id]);






if(loading){


return (

<div className="
max-w-5xl
mx-auto
">

<div className="
h-40
bg-slate-100
rounded-2xl
animate-pulse
"/>

</div>


)

}







if(!document){


return (

<div className="text-center">

<p>
Document not found
</p>


<Link
to="/documents"
className="
text-indigo-600
"
>

Back

</Link>


</div>

)

}








return (

<div className="
max-w-5xl
mx-auto
space-y-8
">





{/* Header */}



<div>


<Link

to="/documents"

className="
text-sm
text-indigo-600
"

>

← Documents

</Link>




<h1 className="
text-3xl
font-bold
text-slate-900
mt-4
">

{document.filename}

</h1>


<p className="
text-slate-500
mt-2
">

{document.doc_type || "Document"}

</p>


</div>








{/* Processing Card */}



<div className="
bg-white
border
border-slate-200
rounded-2xl
p-6
shadow-sm
">


<div className="
flex
justify-between
items-center
">


<h2 className="
font-bold
text-slate-800
">

Processing Status

</h2>



<span className="
text-sm
font-semibold
text-indigo-600
">

{status?.status}

</span>



</div>





<div className="
mt-5
">


<div className="
flex
justify-between
text-xs
text-slate-400
mb-2
">


<span>

{status?.processing_step}

</span>


<span>

{status?.progress || 0}%

</span>



</div>



<div className="
w-full
h-3
bg-slate-100
rounded-full
overflow-hidden
">


<div

style={{
width:`${status?.progress || 0}%`
}}

className="
h-full
bg-indigo-600
transition-all
"

/>


</div>



</div>






{
status?.error_message && (

<div className="
mt-5
p-4
rounded-xl
bg-rose-50
text-rose-700
text-sm
">

{status.error_message}

</div>


)

}



</div>









{/* Extracted Text */}




<div className="
bg-white
border
border-slate-200
rounded-2xl
shadow-sm
p-6
">



<h2 className="
font-bold
text-slate-800
mb-4
">

Extracted Text

</h2>




{

document.extracted_text ? (


<div className="
max-h-96
overflow-y-auto
bg-slate-50
rounded-xl
p-5
text-sm
text-slate-700
whitespace-pre-wrap
">


{document.extracted_text}


</div>



)

:

(

<p className="
text-sm
text-slate-400
">

Text extraction not available yet.

</p>

)

}



</div>









{/* Future Chat */}



<div className="
bg-indigo-50
rounded-2xl
p-6
flex
justify-between
items-center
">


<div>

<h3 className="
font-bold
text-slate-900
">

Ask AI about this document

</h3>


<p className="
text-sm
text-slate-600
mt-1
">

Chat with your uploaded knowledge.

</p>


</div>



<button
  onClick={openChat}
  disabled={document.status !== "processed"}
  className="
    px-5
    py-3
    rounded-xl
    bg-indigo-600
    text-white
    font-semibold
    disabled:opacity-40
  "
>
  Open Chat
</button>




</div>





</div>


)


}