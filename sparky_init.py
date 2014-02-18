def initialize_session(session):

  def rl_command(s = session):
    import openreload
    openreload.show_file_dialog(s)  
    
  session.add_command("rl", "Open and reload spectra (rl)", rl_command)
