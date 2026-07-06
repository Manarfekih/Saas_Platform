import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import api from "../api/auth";
import { useAuth } from "../context/AuthContext";



export default function UploadPage(){


const { token } = useAuth();

const navigate = useNavigate();



const [file,setFile] =
useState<File|null>(null);


const [loading,setLoading] =
useState(false);


const [error,setError] =
useState("");





function handleFileChange(
e:React.ChangeEvent<HTMLInputElement>
){


setError("");


const selected =
e.target.files?.[0];


if(!selected)
return;



const allowed = [

"pdf",
"docx",
"txt"

];


const extension =
selected.name
.split(".")
.pop()
?.toLowerCase();



if(!allowed.includes(extension || "")){


setError(
"Only PDF, DOCX and TXT files are allowed"
);


setFile(null);

return;

}



setFile(selected);



}








async function uploadDocument(){



if(!file)
{

setError(
"Please select a file first"
);

return;

}



if(!token)
return;



try{


setLoading(true);


setError("");



const formData =
new FormData();


formData.append(
"file",
file
);





const res =
await api.post(
"/documents/upload",
formData,
{

headers:{

Authorization:
`Bearer ${token}`,

"Content-Type":
"multipart/form-data"

}

}

);




const documentId =
res.data.document.id;



navigate(
`/documents/${documentId}`
);



}

catch(err:any){


console.error(err);



setError(

err.response?.data?.detail ||

"Upload failed"

);


}

finally{

setLoading(false);

}


}









return (


<div className="
max-w-3xl
mx-auto
space-y-8
">





{/* Header */}


<div>


<Link

to="/dashboard"

className="
text-sm
text-indigo-600
"

>

← Dashboard

</Link>



<h1 className="
text-3xl
font-bold
text-slate-900
mt-4
">

Upload Document

</h1>



<p className="
text-slate-500
mt-2
">

Upload a document and let AI analyze it.

</p>


</div>








{/* Upload box */}



<div className="
bg-white
border
border-slate-200
rounded-2xl
shadow-sm
p-8
">





<label

className="
block
border-2
border-dashed
border-slate-300
rounded-2xl
p-10
text-center
cursor-pointer
hover:border-indigo-400
transition
"

>


<input

type="file"

className="hidden"

onChange={handleFileChange}

/>



{


file ? (


<div>


<p className="
font-semibold
text-slate-800
">

{file.name}

</p>


<p className="
text-sm
text-slate-400
mt-2
">

Ready to upload

</p>


</div>



)


:

(

<div>


<p className="
font-semibold
text-slate-700
">

Click to select file

</p>


<p className="
text-sm
text-slate-400
mt-2
">

PDF, DOCX, TXT supported

</p>


</div>


)


}





</label>







{

error && (

<div className="
mt-5
bg-rose-50
text-rose-700
rounded-xl
p-4
text-sm
">

{error}

</div>

)

}







<button


onClick={uploadDocument}


disabled={loading}


className="
mt-6
w-full
bg-indigo-600
text-white
py-3
rounded-xl
font-semibold
hover:bg-indigo-700
disabled:opacity-50
transition
"

>


{


loading

?

"Uploading..."

:

"Upload Document"


}



</button>






</div>








{/* Info */}



<div className="
grid
md:grid-cols-3
gap-5
">



<div className="
bg-slate-50
rounded-xl
p-5
">

<p className="
font-semibold
text-slate-800
">

Extraction

</p>


<p className="
text-sm
text-slate-500
mt-2
">

AI extracts document content.

</p>


</div>





<div className="
bg-slate-50
rounded-xl
p-5
">

<p className="
font-semibold
text-slate-800
">

Classification

</p>


<p className="
text-sm
text-slate-500
mt-2
">

Detects document type.

</p>


</div>





<div className="
bg-slate-50
rounded-xl
p-5
">

<p className="
font-semibold
text-slate-800
">

AI Chat

</p>


<p className="
text-sm
text-slate-500
mt-2
">

Ask questions later.

</p>


</div>





</div>





</div>


)

}