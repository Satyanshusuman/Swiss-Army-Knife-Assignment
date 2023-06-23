from django.shortcuts import render
import pandas as pd
from django.views import View 
from script.views import extract_key_value_pairs          
from django.contrib import messages
import os 
class  Load_Extract(View):
    
    def get (self,request):
        return render(request,"upload.html")
    
    def post(self,request):
        try:
            file = request.FILES['pdf_file']
            uploaded_file_path=os.path.relpath(file.name)

            data=extract_key_value_pairs(uploaded_file_path)

            df = pd.DataFrame(data['table'])
            header_row = pd.Series(data['header'])
            final_df = pd.concat([header_row.to_frame().T, df], ignore_index=True).fillna("")
            
            table_html = final_df.to_html(index=False)
            return render(request, 'extract.html', {"table_html":table_html})
        except:
            msg=messages.warning(request,"please upload correct file")
            return render (request,"upload.html",{"msg":msg})

