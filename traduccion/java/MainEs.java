package gov.sandia.bioram;

import gov.sandia.bioram.classes.model.RamModel;
import gov.sandia.bioram.classes.model.randomclasses.RamFileMarshal;
import gov.sandia.bioram.forms.ResponseForm;
import java.io.File;
import java.util.Arrays;
import java.util.Locale;
import javax.swing.JOptionPane;
import javax.swing.UIManager;

/**
 * Punto de entrada que abre un modelo en español de forma explícita.
 *
 * El arranque original (gov.sandia.bioram.Main) ignora los argumentos y deja
 * que ResponseForm busque un modelo por su cuenta: recorre el directorio de
 * trabajo y carga el PRIMER archivo .raml que encuentra. En una carpeta con
 * Biosafety.raml y Biosafety_es.raml gana el inglés, porque '.' va antes que
 * '_' al ordenar, y el programa aparece con la interfaz en español pero el
 * cuestionario en inglés, sin avisar.
 *
 * Aquí el modelo se elige a propósito: el que venga como argumento o, si no
 * viene ninguno, un archivo *_es.raml de la carpeta del programa. Si no se
 * encuentra, abre vacío y lo dice, en vez de cargar otro idioma en silencio.
 *
 * También fija el idioma en español de México. La interfaz se toma del idioma
 * del sistema, así que en un Windows en inglés saldría en inglés; y se usa
 * es_MX, no "es" a secas, porque el español de España escribe los decimales con
 * coma y los puntajes de BioRAM se leerían mal ("2,488" en vez de "2.488").
 */
public class MainEs {

  private static final String SUFIJO_ES = "_es.raml";

  /** Modelos de esta traducción, por orden de preferencia. */
  private static final String[] MODELOS = { "Biosafety_es.raml", "Biosecurity_es.raml" };

  public static void main(final String[] args) {
    // Antes de crear la ventana: initComponents() lee el idioma en este momento.
    Locale.setDefault(new Locale("es", "MX"));

    java.awt.EventQueue.invokeLater(new Runnable() {
      @Override
      public void run() {
        try {
          UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
        } catch (Exception e) {
          System.err.println("Error creating default look and feel - " + e.toString());
        }

        File archivo = (args.length > 0 && !args[0].trim().isEmpty())
            ? resolver(args[0].trim())
            : buscarModeloEnEspanol();

        RamModel modelo = null;
        if (archivo != null) {
          try {
            modelo = new RamFileMarshal(archivo).getRamModel();
            System.out.println("Modelo cargado: " + archivo.getAbsolutePath());
          } catch (Exception e) {
            e.printStackTrace();
            avisar("No se pudo abrir el modelo:\n" + archivo.getAbsolutePath()
                + "\n\nUse Archivo > Abrir perfil para elegir otro.");
          }
        } else {
          avisar("No se encontró ningún modelo en español junto al programa.\n\n"
              + "Copie Biosafety_es.raml o Biosecurity_es.raml a esta carpeta:\n"
              + directorioDelPrograma().getAbsolutePath()
              + "\n\nO use Archivo > Abrir perfil para elegirlo a mano.");
        }

        // Un modelo no nulo evita que ResponseForm busque uno por su cuenta.
        new ResponseForm(modelo != null ? modelo : new RamModel()).setVisible(true);
      }
    });
  }

  /** Busca la ruta tal cual, luego junto al programa, luego en el directorio actual. */
  private static File resolver(String ruta) {
    File[] candidatos = {
      new File(ruta),
      new File(directorioDelPrograma(), ruta),
      new File(new File("."), ruta),
    };
    for (File candidato : candidatos) {
      if (candidato.isFile()) {
        return candidato;
      }
    }
    return new File(ruta); // No existe; el llamador avisa del error con esta ruta.
  }

  private static File buscarModeloEnEspanol() {
    File[] carpetas = { directorioDelPrograma(), new File(".") };

    // Primero por nombre exacto: en una carpeta pueden convivir traducciones
    // antiguas que también acaban en _es.raml y que ordenan antes.
    for (File carpeta : carpetas) {
      for (String nombre : MODELOS) {
        File candidato = new File(carpeta, nombre);
        if (candidato.isFile()) {
          return candidato;
        }
      }
    }

    for (File carpeta : carpetas) {
      File[] encontrados = carpeta.listFiles(new java.io.FilenameFilter() {
        @Override
        public boolean accept(File dir, String nombre) {
          return nombre.toLowerCase().endsWith(SUFIJO_ES);
        }
      });
      if (encontrados != null && encontrados.length > 0) {
        // listFiles() no garantiza el orden; se ordena para que sea siempre el mismo.
        Arrays.sort(encontrados);
        return encontrados[0];
      }
    }
    return null;
  }

  /** Carpeta donde está el .exe o el .jar que se ejecutó. */
  private static File directorioDelPrograma() {
    try {
      File propio = new File(MainEs.class.getProtectionDomain()
          .getCodeSource().getLocation().toURI());
      return propio.isDirectory() ? propio : propio.getParentFile();
    } catch (Exception e) {
      return new File(".");
    }
  }

  private static void avisar(String mensaje) {
    JOptionPane.showMessageDialog(null, mensaje, "BioRAM", JOptionPane.WARNING_MESSAGE);
  }
}
