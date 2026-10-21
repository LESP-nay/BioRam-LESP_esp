/*
 * Reemplaza la clase del mismo nombre del programa original, cuyos textos
 * estaban escritos directo en el código y por eso salían en inglés en los
 * diálogos de abrir y guardar ("RAM Files (*.raml)", "CSV Files (*.csv)",
 * "Images (png|bmp|jpg|jpeg)").
 *
 * Lo único que cambia es de dónde sale el texto: ahora del archivo de idioma,
 * con el texto original en inglés como respaldo por si falta la clave. Las
 * reglas de qué archivos se aceptan quedan exactamente igual.
 */
package gov.sandia.bioram.classes.model.randomclasses;

import java.io.File;
import java.util.MissingResourceException;
import java.util.ResourceBundle;
import javax.swing.filechooser.FileFilter;

public class RamFileFilter extends FileFilter {

  private static String texto(String clave, String porOmision) {
    try {
      return ResourceBundle.getBundle("lang/FormStrings").getString(clave);
    } catch (MissingResourceException e) {
      return porOmision;
    }
  }

  public static class CSVFileFilter extends FileFilter {

    @Override
    public boolean accept(File fp) {
      return fp.getName().endsWith(".csv") || fp.isDirectory();
    }

    @Override
    public String getDescription() {
      return texto("FileFilter_CSV", "CSV Files (*.csv)");
    }
  }

  public static class ImageFileFilter extends FileFilter {

    @Override
    public boolean accept(File fp) {
      return fp.getName().matches(".*(png|bmp|jpg|jpeg)$") || fp.isDirectory();
    }

    @Override
    public String getDescription() {
      return texto("FileFilter_Images", "Images (png|bmp|jpg|jpeg)");
    }

  }

  @Override
  public boolean accept(File fp) {
    return fp.getName().matches(".*\\.(raml|zip)$") || fp.isDirectory();
  }

  @Override
  public String getDescription() {
    return texto("FileFilter_Raml", "RAM Files (*.raml)");
  }
}
