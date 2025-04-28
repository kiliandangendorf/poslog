from nlp.pos import TagComparison
from dataclasses import dataclass
from nlp.pos.tagset_mapping import get_tagset_mapping
import pandas as pd


@dataclass
class GuiLogs:
    idx: int
    log_line: str
    log_line_splitted: list[str]
    tag_comparison: TagComparison
    majorities_per_line: list[str]
    #masked_splitted_line: list[str]
    # solved if there are no Nones anymore
    manual_tags: list[str]



root=None
frame=None
current_index:int=-1
POSSIBLE_TAGS:list[str]=None

inited=False

tagged_examples:pd.DataFrame=None
manually_tagged:list[list[str]]=None
majorities:list[list[str]]=None
gui_logs:list[GuiLogs]=None
OUTPUT_FILE:str=None

FIND_NONE_ONLY:bool=False





def get_possible_tags():
    global POSSIBLE_TAGS
    # use this mapping to get the possible tags (no matter if its brown mapping or not)
    POSSIBLE_TAGS=sorted(list(set(get_tagset_mapping('brown_upos').values())))

    def append_possible_tags_from_majorities(majorities:list[list[str]], tag_list:list[str]):
        list_of_all_tags=[mm for m in majorities for mm in m if mm]
        tagset=set(tag_list)
        tagset.update(list_of_all_tags)
        return sorted(list(tagset))

    POSSIBLE_TAGS=append_possible_tags_from_majorities(majorities, POSSIBLE_TAGS)
    print(f"Possible tags: {POSSIBLE_TAGS}")


def initialize_gui(tagged_examples_df:pd.DataFrame,manually_tagged_ls:list[list[str]],majorities_ls:list[list[str]],gui_logs_ls:list[GuiLogs],output_file_str:str,find_none_only:bool=FIND_NONE_ONLY):
    global tagged_examples, manually_tagged, majorities, gui_logs, OUTPUT_FILE, FIND_NONE_ONLY,inited
    tagged_examples=tagged_examples_df
    manually_tagged=manually_tagged_ls
    majorities=majorities_ls
    gui_logs=gui_logs_ls
    OUTPUT_FILE=output_file_str
    FIND_NONE_ONLY=find_none_only

    get_possible_tags()
    inited=True



def update_and_save_tagged_examples_df():
    global tagged_examples
    still_nones=[]
    for pl in gui_logs:
        manually_tagged[pl.idx]=pl.manual_tags
        if None in pl.manual_tags:
            still_nones.append(pl.idx)
            print(f"WARNING: Index {pl.idx} still has Nones.")
    tagged_examples['ManualTagging']=manually_tagged
    tagged_examples.to_csv(OUTPUT_FILE, index=False)
    return OUTPUT_FILE, still_nones




######################
# GUI
######################

import tkinter as tk
from tkinter import messagebox
from collections import Counter


def save_results():
    file, still_nones=update_and_save_tagged_examples_df()
    message=f"Results saved to '{file}'."
    if still_nones:
        message+=f"\n\nWARNING: The following indices still have Nones: {still_nones}"
    messagebox.showinfo("Save Complete", message)

######################
# Navigate
######################
def find_next_index(cur_idx, asc=True, unsolved=False)->int:
    if unsolved:
        if asc:
            for i in range(cur_idx+1, len(gui_logs)):
                if None in gui_logs[i].manual_tags:
                    return i
                if FIND_NONE_ONLY:
                    continue
                for j in range(len(gui_logs[i].manual_tags)):
                    if gui_logs[i].manual_tags[j]!=gui_logs[i].majorities_per_line[j]:
                        return i
                
        else:
            for i in range(cur_idx-1, -1, -1):
                if None in gui_logs[i].manual_tags:
                    return i
                if FIND_NONE_ONLY:
                    continue
                for j in range(len(gui_logs[i].manual_tags)):
                    if gui_logs[i].manual_tags[j]!=gui_logs[i].majorities_per_line[j]:
                        return i
    else:
        if asc:
            cur_idx+=1
        else:
            cur_idx-=1
        if 0 <= cur_idx < len(gui_logs):
            return cur_idx
    return -1

def process_next(asc=True, unsolved=False)->int:
    global current_index
    
    next_index = find_next_index(current_index, asc, unsolved)
    
    if  next_index != -1:
        current_index = next_index
        display_case(gui_logs[current_index])
        return next_index
    else:
        # messagebox.showinfo("End of Loglines", "You have reached the end of the loglines. I will save them and close myself.")
        # save_results()
        # root.quit()
        # root.destroy()
        if messagebox.askyesno("End of Loglines", "You have reached the end of the loglines. Do you want to save them and close?"):
            save_results()
            root.quit()
            root.destroy()
        else:
            display_case(gui_logs[0])
            return 0
def get_next()->int:
    return process_next(asc=True)
def get_next_unsolved()->int:
    return process_next(asc=True, unsolved=True)
def get_previous()->int:
    return process_next(False)
def get_previous_unsolved()->int:
    return process_next(False, unsolved=True)

######################
# Set Tag
######################
def cur_index_solved()->bool:
    return None not in gui_logs[current_index].manual_tags

TAG_NONE='-----' #'_NONE_'
BG_COLOR='#ececec'  # RGB 236, 236, 236 in hexadecimal

#def set_tag(token_index:int, tag:str, label:tk.Label, checkbutton_var:tk.BooleanVar):
def set_tag(token_index:int, tag:str, string_var:tk.StringVar, checkbutton_var:tk.BooleanVar):
    global gui_logs
    if tag.strip() == '' or tag.strip()==TAG_NONE:
        tag=None
    gui_logs[current_index].manual_tags[token_index] = tag

    # update label
    #label.config(text=tag)
    string_var.set(tag)
    if tag is None or tag==TAG_NONE:
        #label.config(text='')
        #string_var.set('')
        string_var.set(TAG_NONE)
    # check if all tags are solved
    checkbutton_var.set(cur_index_solved())        


######################
# Render
######################
def display_case(gui_log:GuiLogs, dropdowns_for_all=True):
    for widget in frame.winfo_children():
        widget.destroy()

    # Display Context
    context_frame=tk.Frame(frame)
    context_frame.pack(anchor='w')
    checkbutton_var = tk.BooleanVar(value=cur_index_solved())
    checkbutton = tk.Checkbutton(context_frame,variable=checkbutton_var,onvalue=True,offvalue=False,state="disabled")
    checkbutton.grid(row=0, column=0, sticky="w")

    frame.config(bg='green' if checkbutton_var.get() else BG_COLOR)
    checkbutton_var.trace_add("write", lambda *args: frame.config(bg='green' if checkbutton_var.get() else BG_COLOR))

    # Input for specific index navigation
    #tk.Label(context_frame, text="Go to index:").grid(row=0, column=0, sticky="w")
    index_var = tk.StringVar(value=str(gui_log.idx))
    index_entry = tk.Entry(context_frame, textvariable=index_var, width=5)
    index_entry.grid(row=0, column=0, sticky="w")

    def go_to_index():
        if not index_var.get().isdigit():
            return
        try:
            idx = int(index_var.get())
            if 0 <= idx < len(gui_logs):
                global current_index
                current_index = idx
                display_case(gui_logs[current_index])
            else:
                messagebox.showerror("Invalid Index", f"Index must be between 0 and {len(gui_logs) - 1}.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid integer index.")

    index_entry.bind("<Return>", lambda event: go_to_index())

    
    tk.Label(context_frame, text=f"Logline #{gui_log.idx}: {gui_log.log_line}", anchor='w').grid(row=0, column=1, sticky="w")
    #.pack(anchor="w")

    tk.Label(context_frame, text=f"(Item {current_index+1} of {len(gui_logs)} in this session)", anchor='w').grid(row=1, column=1, sticky="w")
    #pack(anchor="w", pady=(0, 20))

    
    
    #if parity_logs[current_index].solved_nones.count(None)==0:
        #checked_label=tk.Label(frame, text="All tags have been solved.", anchor='w').pack(anchor="w", pady=(0, 20))

    # Create a canvas for the table with a horizontal scrollbar
    canvas_frame = tk.Frame(frame)
    canvas_frame.pack(fill="x", pady=10)

    table_canvas = tk.Canvas(canvas_frame, height=220)  # Set height for table content
    scrollbar = tk.Scrollbar(canvas_frame, orient="horizontal", command=table_canvas.xview)
    scrollbar.pack(side="bottom", fill="x")
    table_canvas.configure(xscrollcommand=scrollbar.set)

    # Create a table frame inside the canvas
    table_frame = tk.Frame(table_canvas)
    table_canvas.create_window((0, 0), window=table_frame, anchor="nw")
    table_canvas.pack(side="left", fill="both", expand=True)

    def _on_mousewheel(event):
        #table_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        table_canvas.xview_scroll(event.delta*-1, "units")
    table_canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    tag_vars=[]
    # Table and Buttons
    for i, (token, majority_tag, tc_majority, solved_none, tc_minority_tags, tc_confidence) in enumerate(zip(gui_log.log_line_splitted, gui_log.majorities_per_line, gui_log.tag_comparison.majority, gui_log.manual_tags, gui_log.tag_comparison.minority, gui_log.tag_comparison.confidence)):
        tk.Label(table_frame, text=f'{token}\n({majority_tag})').grid(row=0, column=i)
        #tk.Label(table_frame, text=f'{token}').grid(row=0, column=i)
        #tk.Label(table_frame, text=majority_tag).grid(row=1, column=i)

        tag_var = tk.StringVar(value=solved_none or TAG_NONE)
        tag_vars.append(tag_var)

        #tag_label=tk.Label(table_frame, text=solved_none)
        tag_label=tk.Label(table_frame, textvariable=tag_var)
        tag_label.grid(row=1, column=i)

        
        def update_tag_label_color(tag_var, label):
            if tag_var.get()==TAG_NONE:label.config(bg='red')
            elif tag_var.get()!=majority_tag:label.config(bg='LightGoldenrod1')
            else:label.config(bg=BG_COLOR) #fg='black')

        tag_var.trace_add('write', lambda *args, t=tag_var, l=tag_label: update_tag_label_color(t, l))
        update_tag_label_color(tag_var, tag_label)  # Ensure color updates on first render

        if majority_tag is None or dropdowns_for_all:
            btn_frame = tk.Frame(table_frame)
            btn_frame.grid(row=2, column=i, sticky="s")

            if tc_majority is not None:
                tk.Button(btn_frame, text=f"{tc_majority}",
                    command=lambda t=tc_majority, l=tag_var, c=checkbutton_var, i=i: set_tag(i, t, l, c)).pack(anchor="center")

            # Majority Button
            if majority_tag is not None:
                tag=tc_majority                
                tk.Button(btn_frame, text=f"{tag} ({tc_confidence})",
                            command=lambda t=tag, l=tag_var, c=checkbutton_var, i=i: set_tag(i, t, l, c)).pack(anchor="center")
                            # Minority Tag Buttons
            if tc_minority_tags:
                tag_set=set(tc_minority_tags.values())
                # for tag in sorted(tag_set):
                #     tk.Button(btn_frame, text=f"{tag}",
                #               command=lambda t=tag, l=tag_var, c=checkbutton_var, i=i: set_tag(i, t, l, c)).pack(anchor="center")
                tag_counter=Counter(tc_minority_tags.values())
                for tag, c in sorted(tag_counter.items()):
                    tk.Button(btn_frame, text=f"{tag}",
                              command=lambda t=tag, l=tag_var, c=checkbutton_var, i=i: set_tag(i, t, l, c)).pack(anchor="center")
                # for tagger, tag in minority_tags.items():
                #     tk.Button(btn_frame, text=f"{tag} ({tagger})",
                #               command=lambda t=tag, l=tag_label, c=checkbutton_var, i=i: set_tag(i, t, l, c)).pack(anchor="center")
            # Custom Input for Undefined Words
            #tk.Label(btn_frame, text="Custom:").pack(anchor="center")
            # entry = tk.Entry(btn_frame, width=10)
            # entry.pack(side="left")
            # tk.Button(btn_frame, text="Set Text",
            #           command=lambda e=entry, l=tag_label, c=checkbutton_var, i=i: set_tag(i, e.get(), l, c)).pack(side='left')#lambda e=entry, idx=i: on_select(idx, e.get())).pack(side="right")
            
            if dropdowns_for_all:
                #tag_label.getvar()
                # Dropdown for other tags
                #tag_var = tk.StringVar(value=tag_label.cget("text"))
                tag_menu = tk.OptionMenu(btn_frame, tag_var, *([TAG_NONE]+POSSIBLE_TAGS), command=lambda t, l=tag_var, c=checkbutton_var, i=i: set_tag(i, t, l, c))

                #max_width = max(len(tag) for tag in POSSIBLE_TAGS)
                #tag_menu.config(width=max_width)            
                tag_menu.pack(anchor="center")
                # Dropdown for other tags
                #tk.OptionMenu(btn_frame, tag_label, *POSSIBLE_TAGS).pack(side="right")

                

       # Update scroll region after adding all widgets
    table_frame.update_idletasks()
    table_canvas.configure(scrollregion=table_canvas.bbox("all"))

 
    nav_frame = tk.Frame(frame)
    nav_frame.pack(fill="y", side='bottom', anchor='center')

    def apply_for_all():
        #for i, (tag, tag_var) in enumerate(zip(gui_log.tag_comparison.majority, tag_vars)):
        for i, (tag, tag_var) in enumerate(zip(gui_log.majorities_per_line, tag_vars)):
            set_tag(i, tag, tag_var, checkbutton_var)
    # Apply All Button
    tk.Button(nav_frame, text="Apply All", command=apply_for_all).grid(row=0, column=2, sticky='e')
                  

    # Previous Button
    tk.Button(nav_frame, text="Previous", command=get_previous).grid(row=1, column=0, sticky='w')
    tk.Button(nav_frame, text="Previous unsolved (<)", command=get_previous_unsolved).grid(row=1, column=1, sticky='w')
    root.bind('<Left>', lambda event: get_previous_unsolved())
    #if current_index==0:
    if find_next_index(current_index, False)==-1:
        tk.Button(nav_frame, text="Previous", state='disabled').grid(row=1, column=0, sticky='w')
    if find_next_index(current_index, False, unsolved=True)==-1:
        tk.Button(nav_frame, text="Previous unsolved (<)", state='disabled').grid(row=1, column=1, sticky='w')
        root.unbind('<Left>')
    # Next Button
    tk.Button(nav_frame, text="Next", command=get_next).grid(row=1, column=3, sticky='e')
    tk.Button(nav_frame, text="Next unsolved (>)", command=get_next_unsolved).grid(row=1, column=4, sticky='e')
    root.bind('<Right>', lambda event: get_next_unsolved())
    #if current_index==len(parity_logs)-1:
    if find_next_index(current_index)==-1:
        tk.Button(nav_frame, text="Next", state='disabled').grid(row=1, column=3, sticky='e')
    if find_next_index(current_index, unsolved=True)==-1:
        tk.Button(nav_frame, text="Next unsolved (>)", state='disabled').grid(row=1, column=4, sticky='e')
        root.unbind('<Right>')

    # Save Button
    tk.Button(nav_frame, text="Save", command=save_results).grid(row=1, column=2, sticky='e')



# GUI Setup
def run_gui():
    global root, frame, current_index

    if inited==False:
        raise ValueError("GUI not initialized. Please call initialize_gui() first.")
    
    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", lambda: (root.quit(), root.destroy()))

    root.geometry("1200x400")
    root.title("POS Tag Correction Tool")

    frame = tk.Frame(root, padx=10, pady=10)
    frame.pack(fill="both", expand=True)

    current_index = -1
    current_index=process_next(asc=True, unsolved=True)

    #display_case(parity_logs[current_index])

    root.mainloop()
