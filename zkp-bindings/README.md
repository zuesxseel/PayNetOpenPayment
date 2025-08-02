# ZKP Bindings

This directory contains language bindings for the PayNet ZKP biometric authentication system. The bindings allow integration with various platforms and environments.

## Structure

```
zkp-bindings/
├── mobile/          # Mobile platform bindings
│   ├── android/     # Android JNI bindings
│   └── ios/         # iOS FFI bindings
├── nodejs/          # Node.js native addon
└── wasm/            # WebAssembly bindings
```

## Platform Support

### Mobile Bindings (`mobile/`)
- **Android**: JNI bindings for React Native Android
- **iOS**: FFI bindings for React Native iOS
- **Features**: Proof generation, verification, batch operations

### Node.js Bindings (`nodejs/`)
- **Target**: Backend services and APIs
- **Technology**: Neon-rs native addon
- **Features**: Async operations, TypeScript support, batch processing

### WebAssembly Bindings (`wasm/`)
- **Target**: Browser environments
- **Technology**: wasm-bindgen
- **Features**: Client-side proof generation, verification utilities

## Building

### Prerequisites
- Rust 1.70+
- Node.js 16+ (for Node.js bindings)
- Android NDK (for Android bindings)
- Xcode (for iOS bindings)
- wasm-pack (for WASM bindings)

### Build All Bindings
```bash
# From zkp-bindings directory
cargo build --release
```

### Build Specific Platforms

#### Mobile Bindings
```bash
cd mobile
cargo build --release --features android  # For Android
cargo build --release --features ios      # For iOS
```

#### Node.js Bindings
```bash
cd nodejs
npm install
npm run build
```

#### WebAssembly Bindings
```bash
cd wasm
wasm-pack build --target web --release
```

## Usage Examples

### Node.js
```javascript
import { ZKPBiometric, BiometricUtils } from 'zkp-nodejs-bindings';

const zkp = new ZKPBiometric();
await zkp.initialize();

const biometricData = {
  template: [0.1, 0.2, 0.3, 0.4, 0.5],
  metadata: { deviceId: 'device123' }
};

const proof = await zkp.generateProof(biometricData);
const result = await zkp.verifyProof(proof, biometricData);
console.log('Proof valid:', result.isValid);
```

### WebAssembly
```javascript
import init, { ZKPBiometric, WasmBiometricData } from './pkg/zkp_wasm_bindings.js';

await init();

const zkp = new ZKPBiometric();
zkp.initialize();

const template = new Float64Array([0.1, 0.2, 0.3, 0.4, 0.5]);
const biometricData = new WasmBiometricData(template, '{"deviceId": "device123"}');

const proof = zkp.generate_proof(biometricData);
const isValid = zkp.verify_proof(proof, biometricData);
console.log('Proof valid:', isValid);
```

### Android (Java/Kotlin)
```java
// Java
import com.paynet.zkp.ZKPProof;

byte[] biometricData = getBiometricTemplate();
byte[] proof = ZKPProof.generateProof(biometricData);
boolean isValid = ZKPProof.verifyProof(proof, biometricData);
```

### iOS (Swift)
```swift
// Swift
import zkp_ffi

let biometricData = getBiometricTemplate()
let result = zkp_generate_proof(biometricData, biometricData.count)

if result.pointee.success == 1 {
    let proofData = Data(bytes: result.pointee.data_ptr, count: result.pointee.data_len)
    // Use proof data...
}

zkp_free_result(result)
```

## Integration

### React Native
1. Install the mobile bindings package
2. Link native modules
3. Use in TypeScript/JavaScript

### Backend APIs
1. Install Node.js bindings: `npm install zkp-nodejs-bindings`
2. Import and use in Express/Fastify routes
3. Implement batch verification for performance

### Web Applications
1. Bundle WASM module with your app
2. Initialize in web worker for non-blocking operations
3. Use for client-side verification

## Performance Characteristics

| Platform | Proof Generation | Verification | Batch (10 proofs) |
|----------|-----------------|--------------|-------------------|
| Node.js  | ~50ms          | ~30ms        | ~250ms           |
| WASM     | ~80ms          | ~45ms        | ~400ms           |
| Mobile   | ~60ms          | ~35ms        | ~300ms           |

## Security Considerations

1. **Key Management**: Private keys never leave secure environment
2. **Memory Safety**: All bindings use memory-safe operations
3. **Side-channel Resistance**: Constant-time operations where possible
4. **Audit Trail**: All operations are logged for security analysis

## Testing

```bash
# Test all bindings
cargo test

# Test specific platform
cd nodejs && npm test
cd wasm && wasm-pack test --node
```

## Troubleshooting

### Common Issues
1. **Build failures**: Ensure all dependencies are installed
2. **Runtime errors**: Check initialization and data formats
3. **Performance issues**: Use batch operations when possible

### Debug Mode
```bash
# Enable debug logging
RUST_LOG=debug cargo build
```

## Contributing

1. Add new bindings in appropriate platform directories
2. Maintain consistent API across platforms
3. Include comprehensive tests
4. Update documentation

## License

MIT License - see main project LICENSE file.
