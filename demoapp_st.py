import streamlit as st
from img_descriptor import ImgDescriptor
from hp_storage import DataStoragePhysical
from pathlib import Path
import json
from hp_controller import HPController
import base64

import yaml

from ai_client_wrapper import AI_Client_Call_Wrapper

# state_vars = ['obj_stack', 'active', 'stack_init']
# for var in state_vars:
#     if var not in st.session_state:
#         st.session_state[var] = None

st.set_page_config(layout="wide")

base64_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
one_px = base64.b64decode(base64_data)
aiw = None

# # Initialize session state variables
if 'obj_stack' not in st.session_state:
    st.session_state.obj_stack = {} #dict {id: {descript_obj}}

if 'active' not in st.session_state:
    st.session_state.active = None

if 'lng_pref' not in st.session_state:
    st.session_state.lng_pref = 'en'

if 'labels' not in st.session_state:
    st.session_state.labels = None

if 'hpc' not in st.session_state:
    st.session_state.hpc = None

######FUNCIONS##############

@st.cache_resource
def get_ai_wrapper(key):
    aw = AI_Client_Call_Wrapper.make_instructor(key)
    return aw

def get_description(id, aiw):
    # pop_obj = pop_stack(id)
    # pop_obj.ai_wrapper = aiw
    # desc = pop_obj.get_image_description()
    # push_stack(pop_obj)
    pop_obj = st.session_state.hpc.remove_item(id)
    pop_obj.ai_wrapper = aiw
    desc = pop_obj.get_image_description()
    st.session_state.hpc.add_item(pop_obj)


@st.cache_data
def load_stack(data_path):
    j = json.loads(Path(data_path).read_text())
    h = HPController()
    h.load_full_dump(j)
    # st.write(h)
    return h

@st.cache_data
def load_lang_data(lang_path):
    lang_dict = yaml.safe_load(Path.open(lang_path))
    return lang_dict



@st.cache_resource
def load_image_data2(file_bytes, file_name):
    
    idr = ImgDescriptor()
    idr.img_storage = DataStoragePhysical()
    idr.img_storage.load_raw(file_bytes)
    idr.img_storage.uri = file_name
    idr.mime = idr.img_storage.get_mime_type()
    idr.embeddings = ''
    return idr
    


def push_stack(obj):
    # if obj.id not in st.session_state.obj_stack:
    #     # Force Streamlit to detect the change by reassigning
    #     new_stack = st.session_state.obj_stack.copy()
    #     new_stack[obj.id] = obj
    #     st.session_state.obj_stack = new_stack
    #     st.session_state.active = obj.id
    if not st.session_state.hpc.get_item(obj.id):
        st.session_state.hpc.add_item(obj)
    else:
        return None


def pop_stack(id):
    # new_stack = st.session_state.obj_stack.copy()
    # removed_obj = new_stack.pop(id,None)
    # st.session_state.obj_stack = new_stack
    removed_obj = st.session_state.hpc.remove_item(id)
    return removed_obj


def make_active(id):
    # st.session_state.active = id
    st.session_state.hpc.make_active(id)

def get_active_key():
    act = st.session_state.hpc.get_active()
    if act:
        return act.id
    else:
        return False

def check_stack():
    
    if st.session_state.obj_stack is None:
        st.session_state.obj_stack = {}
    st.session_state.obj_stack = dict(st.session_state.obj_stack)
    st.session_state.obj_stack = {idx:obj for idx, obj in st.session_state.obj_stack.items() if obj is not None}
    if st.session_state.active not in st.session_state.obj_stack.keys():
        st.session_state.active = None #list(st.session_state.obj_stack.keys())[0]

######END FUNCIONS##############


# hpc = None
st.session_state.labels = load_lang_data('labels.yaml')
# if not st.session_state.obj_stack:
#     hpc = load_stack('test_data/full_dump.json')
#     st.session_state.hpc = hpc
# if st.session_state.obj_stack is None:
# # if not st.session_state.stack_init:
#     st.session_state.obj_stack = {}
if not st.session_state.hpc:
    st.session_state.hpc = load_stack('test_data/full_dump.json')
    

    



    # for img in hpc.objects_list:
    #     if img.id not in st.session_state.obj_stack:  # Check existence first
    #         img.embeddings = ''
    #         # img.img_storage.raw_data = one_px
    #         st.session_state.obj_stack[img.id] = img
    #     if not st.session_state.active:
    #         st.session_state.active = img.id
        # make_active(img.id)    # st.session_state.stack_init = True
    
    # st.session_state.active = list(st.session_state.obj_stack.keys())[0]
check_stack()    
######FRONT-END##############


#SIDEBAR
with st.sidebar:

    lng_pref = st.sidebar.selectbox(
    st.session_state.labels['lng_pref'][st.session_state.lng_pref],
    ("en", "pl"), index=0    
)
    st.session_state.lng_pref = lng_pref
    
    
    ai_key_inp = st.text_input('AI KEY')

    if ai_key_inp:
        aiw = get_ai_wrapper(ai_key_inp)
        st.write(aiw)

    st.write(st.session_state.hpc)

    



    st.write('Model')
    ai_model_txt = st.sidebar.selectbox(
    st.session_state.labels['ai_model_txt'][st.session_state.lng_pref],
    ("Email", "Home phone", "Mobile phone"))
    
    ai_model_emb = st.sidebar.selectbox(
    st.session_state.labels['ai_model_emb'][st.session_state.lng_pref],
    ("Email", "Home phone", "Mobile phone")
)
    ai_model_gfx = st.sidebar.selectbox(
    st.session_state.labels['ai_model_gfx'][st.session_state.lng_pref],
    ("Email", "Home phone", "Mobile phone")
)
    
  

## SIDEBAR END

st_tab, images_tab, load_tab, active_tab = st.tabs(['Debug',
                                                     st.session_state.labels['images_tab'][st.session_state.lng_pref],
                                                     st.session_state.labels['load_tab'][st.session_state.lng_pref],
                                                     st.session_state.labels['active_tab'][st.session_state.lng_pref]
                                                     ])


with load_tab:
    uploaded_file = st.file_uploader("Upload", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        # Always store the file in session_state using .getvalue()
        st.session_state.last_uploaded_file = uploaded_file.getvalue()

        # Process the stored data
        file_bytes = st.session_state.last_uploaded_file  # No risk of empty reads!
        img_desc = load_image_data2(file_bytes, uploaded_file.name)

        img_desc.id = img_desc.img_storage.hash
        st.write("Computed Hash:", img_desc.id)  #
        push_stack(img_desc)

        
        # st.session_state.active = img_desc.id 
        st.session_state.hpc.make_active(img_desc.id)

        # st.query_params(updated="true")
        # st.session_state.update(active=img_desc.id)

        st.image(img_desc.img_storage.raw_data)
        # st.image(st.session_state.obj_stack[st.session_state['active']].img_storage.raw_data)

        # st.rerun()


with st_tab:
    
    # st.write(st.session_state.obj_stack.keys())
    # st.write([[obj.id, obj.description, obj.img_storage.uri] for idx, obj in  st.session_state.obj_stack.items()])
    # st.write(st.session_state)
    # st.image(st.session_state.obj_stack[st.session_state['active']].img_storage.raw_data)
    hpc_iter = st.session_state.hpc.iter_index()
    st.write([[obj.id, obj.description, obj.img_storage.uri] for idx, obj in  hpc_iter])
    st.write(st.session_state.hpc.active)

with images_tab:
    # if st.session_state.active:
    hpc_iter = st.session_state.hpc.iter_index()
    for kid, img in hpc_iter:
        col1, col2 = st.columns([3, 1])
        with col1:
            # is_active = kid == st.session_state.active
            is_active = get_active_key()
            # st.write(f"ID: {kid} {'⭐' if is_active else ''}")
            # st.image(img.img_storage.raw_data)
            # st.write(img.description)
            # st.write(img.img_storage.uri)
            # if st.session_state.hpc.active.id:
            #     is_active = kid == st.session_state.hpc.active.id
            # else:
            #     is_active = False
            st.write(f"ID: {kid} {'⭐' if is_active == kid else ''}")
            # st.write(f"ID: {kid}")
            st.image(img.img_storage.raw_data)
            st.write(img.description)
            st.write(img.img_storage.uri)
            # is_active = kid == st.session_state.hpc.active.id

        with col2:
            # Add button to make this item active
            st.button(
                # st.session_state.labels['set_active_btn']['lng_pref'][st.session_state.lng_pref]
                f"{st.session_state.labels['set_active_btn'][st.session_state.lng_pref]} {st.session_state.labels['set_active_btn_now'][st.session_state.lng_pref] if is_active == kid else ''}",
                # f"{st.session_state.labels['set_active_btn'][st.session_state.lng_pref]} {st.session_state.labels['set_active_btn_now'][st.session_state.lng_pref]}",
                key=f"active_{kid}",  # Unique key for each button
                on_click=make_active,  # Use our existing method
                args=(kid,),  # Pass the ID to the callback
                # disabled=is_active  # Disable button if already active
            )
            st.button(
                # st.session_state.labels['set_active_btn']['lng_pref'][st.session_state.lng_pref]
                f"DELETE",
                key=f"delete_{kid}",  # Unique key for each button
                on_click=pop_stack,  # Use our existing method
                args=(kid,),  # Pass the ID to the callback
                #disabled=is_active  # Disable button if already active
            )
        # else:
        #     st.write('no act')

with active_tab:
    # act_key = st.session_state['active']
    # if act_key not in st.session_state.obj_stack.keys():
    #     act_key = st.session_state.obj_stack.keys()[0]
    # st.write(act_key)
    if st.session_state.hpc.get_active():
        act_key = get_active_key()

        st.write(act_key)




        img_col, data_col = st.columns(2)
        with img_col:
            # si = st.session_state.obj_stack[act_key]
            # st.image(si.img_storage.raw_data)
            # st.write(st.session_state.obj_stack[st.session_state['active']])
            si = st.session_state.hpc.active
            st.image(si.img_storage.raw_data)
            st.write(st.session_state.hpc.active)

        with data_col:
            
            st.write ([si.id, si.description, si.img_storage.uri, si.mime],)
            
            get_description_btn = st.button(
                    f"{st.session_state.labels['get_description_btn'][st.session_state.lng_pref]}",
                    key=f"description_{act_key}",
                    on_click=get_description,
                    args=(act_key,aiw),
                )
            # st.write(st.session_state.obj_stack[act_key].description)
            st.write(st.session_state.hpc.active.description)

            popped = None
            # if get_description_btn:
            #     popped = pop_stack(act_key)
            #     popped.ai_wrapper = aiw
            #     imd = popped.get_image_description()
            #     st.write(imd)
            #     popped.description = imd.description
            #     popped.tags = imd.tags
            #     push_stack(popped)

            st.download_button(
                                label=f"{st.session_state.labels['download_active_btn'][st.session_state.lng_pref]}",
                                data=si.img_storage.raw_data,
                                file_name=f"{si.img_storage.uri}",
                                mime="si.mime",
                                icon=":material/download:",
                                )
    else:
        st.write('Nothing Active')



